"""H07: lectura del historial propio; no modifica solicitudes ni vigencia."""

from fastapi import APIRouter, Query, Request
from sqlalchemy import func, select

from app import auth, drafts
from app.db import models as m

router = APIRouter(prefix="/api/v1/me/request-history")


def student(conn, request):
    identity = auth.current(conn, request)
    if not identity:
        return None
    return conn.scalar(
        select(m.perfil_estudiante.c.id).where(
            m.perfil_estudiante.c.usuario_id == identity[1]["id"]
        )
    )


def summary(conn, principal):
    versions = m.version_solicitud
    first = conn.scalar(
        select(func.min(versions.c.creado_en)).where(
            versions.c.solicitud_id == principal["id"]
        )
    )
    period = (
        conn.execute(
            select(m.periodo_academico).where(
                m.periodo_academico.c.id == principal["periodo_id"]
            )
        )
        .mappings()
        .one()
    )
    return dict(
        id=principal["id"],
        periodo_id=period["id"],
        periodo=period["identificador"],
        zona_horaria=period["zona_horaria"],
        estado=principal["estado"],
        creado_en=first,
        enviado_en=conn.scalar(
            select(func.max(m.evento_solicitud.c.creado_en)).where(
                m.evento_solicitud.c.solicitud_id == principal["id"],
                m.evento_solicitud.c.tipo == "envio",
            )
        ),
        version_vigente_id=principal["version_vigente_id"],
        version_trabajo_id=principal["version_trabajo_id"],
    )


def version_summary(conn, principal, version):
    events = (
        conn.execute(
            select(m.evento_solicitud)
            .where(
                m.evento_solicitud.c.solicitud_id == principal["id"],
                m.evento_solicitud.c.version_id == version["id"],
            )
            .order_by(m.evento_solicitud.c.id)
        )
        .mappings()
        .all()
    )
    sent = next((e["creado_en"] for e in events if e["tipo"] == "envio"), None)
    transmitted = any(e["tipo"] in ("envio", "fundamento_actualizado") for e in events)
    current = principal["version_vigente_id"] == version["id"]
    invalid = any(e["tipo"] == "invalidacion" for e in events)
    return dict(
        id=version["id"],
        numero=version["numero"],
        malla_id=version["version_malla_id"],
        revision_perfil_id=version["revision_perfil_id"],
        creado_en=version["creado_en"],
        enviado_en=sent,
        tipo="enviada" if transmitted else "borrador",
        estado=(
            "vigente"
            if current
            else "invalidada"
            if invalid
            else "borrador_actual"
            if principal["version_trabajo_id"] == version["id"]
            else "sustituida"
        ),
        vigente=current,
        numero_asignaturas=conn.scalar(
            select(func.count())
            .select_from(m.detalle_solicitud)
            .where(m.detalle_solicitud.c.version_id == version["id"])
        ),
        eventos=[dict(tipo=e["tipo"], registrado_en=e["creado_en"]) for e in events],
    )


def owned(conn, sid, request_id):
    return (
        conn.execute(
            select(m.solicitud).where(
                m.solicitud.c.estudiante_id == sid,
                m.solicitud.c.id == request_id,
            )
        )
        .mappings()
        .first()
    )


@router.get("")
def history(
    request: Request, offset: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=50)
):
    with auth.engine().begin() as conn:
        auth.lock(conn)
        sid = student(conn, request)
        if sid is None:
            return auth.error(401, "sesion_requerida", "Inicia sesión como estudiante.")
        query = select(m.solicitud).where(m.solicitud.c.estudiante_id == sid)
        total = conn.scalar(select(func.count()).select_from(query.subquery()))
        rows = (
            conn.execute(
                query.join(m.periodo_academico)
                .order_by(
                    m.periodo_academico.c.inicio_periodo.desc(), m.solicitud.c.id.desc()
                )
                .offset(offset)
                .limit(limit)
            )
            .mappings()
            .all()
        )
        items = []
        for row in rows:
            vid = row["version_trabajo_id"] or row["version_vigente_id"]
            version = (
                conn.execute(
                    select(m.version_solicitud)
                    .where(
                        m.version_solicitud.c.solicitud_id == row["id"],
                        *([m.version_solicitud.c.id == vid] if vid else []),
                    )
                    .order_by(m.version_solicitud.c.numero.desc())
                    .limit(1)
                )
                .mappings()
                .one()
            )
            items.append(
                dict(**summary(conn, row), version=version_summary(conn, row, version))
            )
        return drafts.response(
            dict(items=items, total=total, offset=offset, limit=limit)
        )


@router.get("/{request_id}/versions")
def versions(
    request: Request,
    request_id: int,
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
):
    with auth.engine().begin() as conn:
        auth.lock(conn)
        sid = student(conn, request)
        if sid is None:
            return auth.error(401, "sesion_requerida", "Inicia sesión como estudiante.")
        principal = owned(conn, sid, request_id)
        if not principal:
            return auth.error(
                404, "solicitud_no_disponible", "Solicitud no disponible."
            )
        query = select(m.version_solicitud).where(
            m.version_solicitud.c.solicitud_id == request_id
        )
        total = conn.scalar(select(func.count()).select_from(query.subquery()))
        rows = (
            conn.execute(
                query.order_by(m.version_solicitud.c.numero.desc())
                .offset(offset)
                .limit(limit)
            )
            .mappings()
            .all()
        )
        return drafts.response(
            dict(
                solicitud=summary(conn, principal),
                items=[version_summary(conn, principal, v) for v in rows],
                total=total,
                offset=offset,
                limit=limit,
            )
        )


@router.get("/{request_id}/versions/{version_id}")
def detail(request: Request, request_id: int, version_id: int):
    with auth.engine().begin() as conn:
        auth.lock(conn)
        sid = student(conn, request)
        if sid is None:
            return auth.error(401, "sesion_requerida", "Inicia sesión como estudiante.")
        principal = owned(conn, sid, request_id)
        version = (
            conn.execute(
                select(m.version_solicitud).where(
                    m.version_solicitud.c.solicitud_id == request_id,
                    m.version_solicitud.c.estudiante_id == sid,
                    m.version_solicitud.c.id == version_id,
                )
            )
            .mappings()
            .first()
        )
        if not principal or not version:
            return auth.error(404, "version_no_disponible", "Versión no disponible.")
        return drafts.response(
            dict(
                solicitud=summary(conn, principal),
                version=version_summary(conn, principal, version),
                selecciones=drafts.version_data(conn, version_id)["selecciones"],
            )
        )
