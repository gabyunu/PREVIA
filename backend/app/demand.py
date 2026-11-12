"""H06: agregados administrativos de versiones vigentes, sin datos personales."""

import csv
import io
from typing import Literal

from fastapi import APIRouter, Query, Request
from fastapi.responses import Response
from sqlalchemy import and_, select

from app import auth
from app.db import models as m
from app.drafts import response

router = APIRouter(prefix="/api/v1/admin")
WARNING = (
    "Demanda autodeclarada y provisional; no acredita elegibilidad oficial, "
    "matrícula ni disponibilidad. Grupos orientativos, no oferta académica oficial."
)


def authorize(conn, request):
    identity = auth.current(conn, request)
    if not identity:
        return auth.error(
            401, "sesion_requerida", "Inicia sesión para consultar Demanda."
        )
    if "administrador" not in auth.user_data(conn, identity[1])["roles"]:
        return auth.error(
            403, "permiso_requerido", "Demanda requiere autorización administrativa."
        )
    return None


def aggregate(conn, period_id, curriculum_id, query, semester, priority, order, size):
    # Una sola consulta de hechos: nunca unir eventos ni versiones de trabajo.
    source = m.solicitud.join(
        m.version_solicitud,
        and_(
            m.solicitud.c.version_vigente_id == m.version_solicitud.c.id,
            m.solicitud.c.id == m.version_solicitud.c.solicitud_id,
        ),
    ).join(
        m.detalle_solicitud,
        m.detalle_solicitud.c.version_id == m.version_solicitud.c.id,
    )
    source = source.join(
        m.malla_asignatura,
        m.malla_asignatura.c.id == m.detalle_solicitud.c.malla_asignatura_id,
    )
    source = source.join(
        m.version_malla, m.version_malla.c.id == m.version_solicitud.c.version_malla_id
    )
    source = source.join(
        m.periodo_academico, m.periodo_academico.c.id == m.solicitud.c.periodo_id
    )
    source = source.outerjoin(
        m.planificacion_cupos,
        and_(
            m.planificacion_cupos.c.periodo_id == m.solicitud.c.periodo_id,
            m.planificacion_cupos.c.malla_asignatura_id == m.malla_asignatura.c.id,
        ),
    )
    statement = (
        select(
            m.solicitud.c.estudiante_id,
            m.solicitud.c.periodo_id,
            m.periodo_academico.c.identificador.label("periodo"),
            m.version_solicitud.c.version_malla_id.label("malla_id"),
            m.version_malla.c.codigo_version.label("malla"),
            m.version_solicitud.c.fundamento,
            m.malla_asignatura.c.id.label("asignatura_id"),
            m.malla_asignatura.c.nombre_publicado.label("nombre"),
            m.malla_asignatura.c.codigo_publicado.label("codigo"),
            m.malla_asignatura.c.semestre_curricular.label("semestre"),
            m.detalle_solicitud.c.prioridad,
            m.planificacion_cupos.c.cupos_planificados,
        )
        .select_from(source)
        .where(m.solicitud.c.estado == "enviada")
    )
    if period_id:
        statement = statement.where(m.solicitud.c.periodo_id == period_id)
    if curriculum_id:
        statement = statement.where(
            m.version_solicitud.c.version_malla_id == curriculum_id
        )
    rows, students, semesters = {}, set(), {}
    for fact in conn.execute(statement).mappings():
        snapshot = next(
            (
                s
                for s in (fact["fundamento"] or {}).get("materias", [])
                if s["malla_asignatura_id"] == fact["asignatura_id"]
            ),
            {},
        )
        name = snapshot.get("nombre", fact["nombre"])
        term = snapshot.get("semestre_curricular", fact["semestre"])
        if (
            query.casefold()
            not in f"{name} {fact['codigo'] or ''} {fact['asignatura_id']}".casefold()
            or (semester and term != semester)
            or (priority and fact["prioridad"] != priority)
        ):
            continue
        key = (fact["periodo_id"], fact["malla_id"], fact["asignatura_id"])
        if key not in rows:
            rows[key] = {
                k: fact[k]
                for k in (
                    "periodo_id",
                    "periodo",
                    "malla_id",
                    "malla",
                    "asignatura_id",
                    "codigo",
                    "cupos_planificados",
                )
            }
            rows[key].update(
                nombre=name,
                semestre=term,
                total=0,
                alta=0,
                media=0,
                baja=0,
                repeticion=0,
            )
        row = rows[key]
        row["total"] += 1
        row[fact["prioridad"]] += 1
        row["repeticion"] += snapshot.get("estado_declarado") == "reprobada"
        students.add(fact["estudiante_id"])
        summary = semesters.setdefault(term, {"students": set(), "total": 0})
        summary["students"].add(fact["estudiante_id"])
        summary["total"] += 1
    result = list(rows.values())
    for row in result:
        row["grupos"] = (row["total"] + size - 1) // size if size else None
    keys = {
        "descending": lambda r: (
            -r["total"],
            r["nombre"],
            r["periodo_id"],
            r["malla_id"],
        ),
        "ascending": lambda r: (
            r["total"],
            r["nombre"],
            r["periodo_id"],
            r["malla_id"],
        ),
        "name": lambda r: (r["nombre"], r["periodo_id"], r["malla_id"]),
        "semester": lambda r: (
            r["semestre"],
            r["nombre"],
            r["periodo_id"],
            r["malla_id"],
        ),
    }
    result.sort(key=keys[order])
    return dict(
        semestres=[
            dict(
                semestre=term,
                estudiantes=len(summary["students"]),
                intenciones=summary["total"],
            )
            for term, summary in sorted(semesters.items())
        ],
        generado_en=auth.now().isoformat() + "Z",
        aviso=WARNING,
        filas=result,
        estudiantes=len(students),
        intenciones=sum(r["total"] for r in result),
        alta=sum(r["alta"] for r in result),
        media=sum(r["media"] for r in result),
        baja=sum(r["baja"] for r in result),
        asignaturas=len({(r["malla_id"], r["asignatura_id"]) for r in result}),
    )


@router.get("/demand/options")
def options(request: Request):
    with auth.engine().begin() as conn:
        denied = authorize(conn, request)
        if denied:
            return denied
        return response(
            dict(
                periodos=[
                    dict(r)
                    for r in conn.execute(
                        select(
                            m.periodo_academico.c.id,
                            m.periodo_academico.c.identificador,
                        ).order_by(m.periodo_academico.c.id)
                    ).mappings()
                ],
                mallas=[
                    dict(r)
                    for r in conn.execute(
                        select(
                            m.version_malla.c.id, m.version_malla.c.codigo_version
                        ).order_by(m.version_malla.c.id)
                    ).mappings()
                ],
            )
        )


def safe_cell(value):
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


@router.get("/demand")
def demand(
    request: Request,
    periodo_id: int | None = Query(None, gt=0),
    malla_id: int | None = Query(None, gt=0),
    q: str = Query("", max_length=255),
    semestre: int | None = Query(None, gt=0),
    prioridad: Literal["alta", "media", "baja"] | None = None,
    orden: Literal["descending", "ascending", "name", "semester"] = "descending",
    tamano_grupo: int | None = Query(None, gt=0, le=1000000),
    formato: Literal["json", "csv"] = "json",
):
    with auth.engine().begin() as conn:
        denied = authorize(conn, request)
        if denied:
            return denied
        data = aggregate(
            conn, periodo_id, malla_id, q, semestre, prioridad, orden, tamano_grupo
        )
    if formato == "json":
        return response(data)
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["Generado UTC", data["generado_en"]])
    writer.writerow([WARNING])
    writer.writerow(
        [
            "Filtros",
            safe_cell(q),
            periodo_id,
            malla_id,
            semestre,
            prioridad,
            orden,
            tamano_grupo,
        ]
    )
    writer.writerow(
        [
            "Estudiantes únicos",
            data["estudiantes"],
            "Intenciones",
            data["intenciones"],
            "Alta",
            data["alta"],
            "Media",
            data["media"],
            "Baja",
            data["baja"],
            "Asignaturas con demanda",
            data["asignaturas"],
        ]
    )
    fields = [
        "periodo_id",
        "periodo",
        "malla_id",
        "malla",
        "asignatura_id",
        "codigo",
        "nombre",
        "semestre",
        "total",
        "alta",
        "media",
        "baja",
        "repeticion",
        "cupos_planificados",
        "grupos",
    ]
    writer.writerow(fields)
    for row in data["filas"]:
        writer.writerow(
            [safe_cell(row[f]) if row[f] is not None else "Desconocido" for f in fields]
        )
    return Response(
        "\ufeff" + output.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={
            "Cache-Control": "no-store",
            "Content-Disposition": 'attachment; filename="PREVIA-demanda.csv"',
        },
    )
