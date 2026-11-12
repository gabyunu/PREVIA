"""H04-A: catálogo piloto provisional y revisiones académicas propias."""

import hmac
from typing import Literal

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import insert, select, update

from app import auth
from app.db import models as m
from app.eligibility import evaluate

router = APIRouter(prefix="/api/v1")
WARNING = (
    "Malla piloto provisional y no oficial. "
    "Historial autodeclarado, no verificado por la universidad."
)


class StateBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    malla_asignatura_id: int = Field(gt=0, strict=True)
    estado: Literal["aprobada", "reprobada", "no_cursada"]


class ProfileBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    revision_esperada: int = Field(ge=0, strict=True)
    malla_id: int = Field(gt=0, strict=True)
    semestre_declarado: int = Field(gt=0, strict=True)
    estados: list[StateBody] = Field(max_length=53)


def pilot(conn):
    # Excepción H04-A: lectura del borrador existente, sin publicarlo.
    return (
        conn.execute(
            select(m.version_malla)
            .join(m.carrera)
            .where(m.carrera.c.codigo == "DEMO-PILOTO-NO-OFICIAL")
        )
        .mappings()
        .all()
    )


def latest(conn, student):
    return (
        conn.execute(
            select(m.revision_perfil)
            .where(m.revision_perfil.c.estudiante_id == student)
            .order_by(m.revision_perfil.c.numero.desc())
            .limit(1)
        )
        .mappings()
        .first()
    )


def profile_data(conn, revision):
    if not revision:
        return dict(revision=0, malla_id=None, semestre_declarado=None, estados=[])
    states = (
        conn.execute(
            select(
                m.estado_academico_declarado.c.malla_asignatura_id,
                m.estado_academico_declarado.c.estado,
            )
            .where(m.estado_academico_declarado.c.revision_perfil_id == revision["id"])
            .order_by(m.estado_academico_declarado.c.malla_asignatura_id)
        )
        .mappings()
        .all()
    )
    return dict(
        revision=revision["numero"],
        malla_id=revision["version_malla_id"],
        semestre_declarado=revision["semestre_declarado"],
        estados=[dict(s) for s in states],
    )


@router.get("/careers")
def careers(request: Request):
    return academic(request, resource="careers")


@router.get("/curricula")
def curricula(request: Request, career_id: int | None = None):
    return academic(request, resource="curricula", career_id=career_id)


@router.get("/curricula/{curriculum_id}")
def curriculum(request: Request, curriculum_id: int):
    return academic(request, resource="curriculum", curriculum_id=curriculum_id)


@router.get("/me/eligibility")
def get_eligibility(request: Request):
    return academic(request, resource="eligibility")


@router.get("/me/academic-profile")
def get_profile(request: Request):
    return academic(request)


@router.put("/me/academic-profile")
def put_profile(request: Request, body: ProfileBody):
    return academic(request, body=body)


def academic(
    request, body=None, resource="profile", curriculum_id=None, career_id=None
):
    with auth.engine().begin() as conn:
        # Mismo orden de bloqueo que identidad; luego perfil propio.
        auth.lock(conn)
        identity = auth.current(conn, request)
        if not identity:
            return auth.error(401, "sesion_requerida", "Inicia sesión para continuar.")
        session, user = identity
        student = conn.scalar(
            select(m.perfil_estudiante.c.id)
            .where(m.perfil_estudiante.c.usuario_id == user["id"])
            .with_for_update()
        )
        if student is None:
            return auth.error(
                403, "perfil_no_disponible", "Se requiere una cuenta de estudiante."
            )
        if resource == "eligibility":
            revision = latest(conn, student)
            if not revision:
                return auth.error(
                    409, "perfil_requerido", "Guarda primero tu perfil académico."
                )
            return JSONResponse(
                dict(evaluate(conn, revision), advertencia=WARNING, provisional=True),
                headers={"Cache-Control": "no-store"},
            )
        versions = pilot(conn)
        if len(versions) != 1:
            return auth.error(
                409, "piloto_no_disponible", "Se requiere una única malla piloto."
            )
        version = versions[0]
        result = None
        revision = latest(conn, student)
        if request.method == "PUT":
            if not auth.origin_ok(request):
                return auth.error(403, "origen_invalido", "Origen no autorizado.")
            if not hmac.compare_digest(
                session["csrf_digest"],
                auth.digest(request.headers.get("x-csrf-token", "")),
            ):
                return auth.error(
                    403, "csrf_invalido", "No se pudo validar la petición."
                )
            if body is None:
                return auth.error(
                    422, "entrada_invalida", "Introduce el perfil completo."
                )
            if revision and body.malla_id != revision["version_malla_id"]:
                return auth.error(
                    409,
                    "cambio_malla_no_habilitado",
                    "El cambio de malla no está habilitado.",
                )
            if body.malla_id != version["id"]:
                return auth.error(
                    422, "fuera_de_malla", "Selecciona la malla piloto disponible."
                )
            current_number = revision["numero"] if revision else 0
            if body.revision_esperada != current_number:
                return auth.error(
                    409,
                    "revision_obsoleta",
                    "El perfil cambió. Recarga el perfil antes de guardar.",
                )
            ids = [s.malla_asignatura_id for s in body.estados]
            if len(set(ids)) != len(ids):
                return auth.error(
                    422,
                    "estados_duplicados",
                    "Una asignatura solo puede tener un estado.",
                )
            allowed = set(
                conn.execute(
                    select(m.malla_asignatura.c.id).where(
                        m.malla_asignatura.c.version_malla_id == body.malla_id
                    )
                ).scalars()
            )
            if not set(ids) <= allowed:
                return auth.error(
                    422,
                    "fuera_de_malla",
                    "Hay asignaturas ajenas a la malla seleccionada.",
                )
            rid = conn.execute(
                insert(m.revision_perfil).values(
                    estudiante_id=student,
                    numero=current_number + 1,
                    version_malla_id=body.malla_id,
                    semestre_declarado=body.semestre_declarado,
                    creado_en=auth.now(),
                )
            ).inserted_primary_key[0]
            if body.estados:
                conn.execute(
                    insert(m.estado_academico_declarado),
                    [
                        dict(
                            revision_perfil_id=rid,
                            version_malla_id=body.malla_id,
                            **s.model_dump(),
                        )
                        for s in body.estados
                    ],
                )
            from app.drafts import revalidate_open

            affected = revalidate_open(conn, student, latest(conn, student))
            result = profile_data(conn, latest(conn, student))
            result.update(
                mensaje="Perfil académico guardado.", solicitudes_afectadas=affected
            )
        elif resource == "profile":
            result = profile_data(conn, revision)
        elif resource == "careers":
            result = [
                dict(
                    conn.execute(
                        select(m.carrera).where(m.carrera.c.id == version["carrera_id"])
                    )
                    .mappings()
                    .one()
                )
            ]
        elif resource == "curricula":
            result = (
                [dict(version, provisional=True, advertencia=WARNING)]
                if career_id in (None, version["carrera_id"])
                else []
            )
        else:
            if curriculum_id != version["id"]:
                return auth.error(404, "malla_no_encontrada", "Malla no disponible.")
            subjects = conn.execute(
                select(m.malla_asignatura)
                .where(m.malla_asignatura.c.version_malla_id == curriculum_id)
                .order_by(
                    m.malla_asignatura.c.semestre_curricular, m.malla_asignatura.c.id
                )
            ).mappings()
            edges = conn.execute(
                select(m.prerrequisito).where(
                    m.prerrequisito.c.version_malla_id == curriculum_id
                )
            ).mappings()
            result = dict(
                version,
                asignaturas=[
                    dict(
                        malla_asignatura_id=s["id"],
                        **{
                            k: s[k]
                            for k in (
                                "asignatura_id",
                                "codigo_publicado",
                                "nombre_publicado",
                                "semestre_curricular",
                            )
                        },
                    )
                    for s in subjects
                ],
                aristas=[
                    dict(
                        asignatura_id=e["asignatura_id"],
                        requisito_id=e["requisito_asignatura_id"],
                    )
                    for e in edges
                ],
            )
        conn.execute(
            update(m.sesion)
            .where(m.sesion.c.id == session["id"])
            .values(ultimo_en=auth.now())
        )
        if isinstance(result, dict):
            result.update(advertencia=WARNING, provisional=True)
        return JSONResponse(result, headers={"Cache-Control": "no-store"})
