"""H05-A: selección propia, validada y transaccional."""

import hmac
from typing import Literal

from fastapi import APIRouter, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import insert, select, update

from app import academic, auth
from app.db import models as m
from app.eligibility import evaluate

router = APIRouter(prefix="/api/v1")


class Selection(BaseModel):
    model_config = ConfigDict(extra="forbid")
    malla_asignatura_id: int = Field(gt=0, strict=True)
    prioridad: Literal["alta", "media", "baja"]


class Draft(BaseModel):
    model_config = ConfigDict(extra="forbid")
    revision_esperada: int = Field(ge=0, strict=True)
    revision_perfil: int = Field(gt=0, strict=True)
    selecciones: list[Selection] = Field(max_length=7)


def response(data):
    return JSONResponse(jsonable_encoder(data), headers={"Cache-Control": "no-store"})


def data(conn, request):
    version = (
        conn.execute(
            select(m.version_solicitud).where(
                m.version_solicitud.c.id == request["version_trabajo_id"]
            )
        )
        .mappings()
        .one()
    )
    selections = (
        conn.execute(
            select(
                m.detalle_solicitud.c.malla_asignatura_id,
                m.detalle_solicitud.c.prioridad,
            )
            .where(m.detalle_solicitud.c.version_id == version["id"])
            .order_by(m.detalle_solicitud.c.malla_asignatura_id)
        )
        .mappings()
        .all()
    )
    return dict(
        id=request["id"],
        periodo_id=request["periodo_id"],
        estado=request["estado"],
        revision_control=request["revision_control"],
        vigente=None,
        trabajo=dict(
            id=version["id"],
            revision_perfil_id=version["revision_perfil_id"],
            malla_id=version["version_malla_id"],
            selecciones=[dict(s) for s in selections],
        ),
    )


@router.get("/periods")
def periods(request: Request):
    with auth.engine().begin() as conn:
        auth.lock(conn)
        if not auth.current(conn, request):
            return auth.error(401, "sesion_requerida", "Inicia sesión para continuar.")
        now = auth.now()
        rows = conn.execute(
            select(m.periodo_academico)
            .where(m.periodo_academico.c.estado_configuracion == "publicado")
            .order_by(m.periodo_academico.c.captura_desde.desc())
        ).mappings()
        return response(
            [
                dict(r, captura_abierta=r["captura_desde"] <= now < r["captura_hasta"])
                for r in rows
            ]
        )


@router.get("/me/requests/{period_id}")
def get_draft(request: Request, period_id: int, allow_empty: bool = False):
    return handle(request, period_id, allow_empty=allow_empty)


@router.put("/me/requests/{period_id}/draft")
def put_draft(request: Request, period_id: int, body: Draft):
    return handle(request, period_id, body)


def handle(request, period_id, body=None, allow_empty=False):
    with auth.engine().begin() as conn:
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
                403, "perfil_requerido", "Se requiere perfil de estudiante."
            )
        period = (
            conn.execute(
                select(m.periodo_academico)
                .where(m.periodo_academico.c.id == period_id)
                .with_for_update()
            )
            .mappings()
            .first()
        )
        if not period or period["estado_configuracion"] != "publicado":
            return auth.error(404, "periodo_no_disponible", "Período no disponible.")
        principal = (
            conn.execute(
                select(m.solicitud)
                .where(
                    m.solicitud.c.estudiante_id == student,
                    m.solicitud.c.periodo_id == period_id,
                )
                .with_for_update()
            )
            .mappings()
            .first()
        )
        if body is None:
            if not principal:
                if allow_empty:
                    return response(None)
                return auth.error(404, "sin_borrador", "Todavía no hay borrador.")
            return response(data(conn, principal))
        if not auth.origin_ok(request) or not hmac.compare_digest(
            session["csrf_digest"], auth.digest(request.headers.get("x-csrf-token", ""))
        ):
            return auth.error(403, "csrf_invalido", "No se pudo validar la petición.")
        if not period["captura_desde"] <= auth.now() < period["captura_hasta"]:
            return auth.error(409, "captura_cerrada", "La captura no está abierta.")
        number = principal["revision_control"] if principal else 0
        revision = academic.latest(conn, student)
        if (
            body.revision_esperada != number
            or not revision
            or body.revision_perfil != revision["numero"]
        ):
            return auth.error(
                409,
                "revision_obsoleta",
                "El borrador o perfil cambió. Recarga antes de guardar.",
            )
        if principal and principal["estado"] != "borrador":
            return auth.error(409, "estado_invalido", "Solicitud no editable en H05-A.")
        ids = [s.malla_asignatura_id for s in body.selecciones]
        if len(ids) != len(set(ids)):
            return auth.error(
                422, "duplicados", "Una asignatura solo puede seleccionarse una vez."
            )
        high = sum(s.prioridad == "alta" for s in body.selecciones)
        if high > 3 or len(ids) - high > 4:
            return auth.error(
                422, "limites_prioridad", "Máximo 3 altas y 4 medias/bajas."
            )
        allowed = {
            r["malla_asignatura_id"]: r for r in evaluate(conn, revision)["materias"]
        }
        for sid in ids:
            if sid not in allowed:
                return auth.error(422, "fuera_de_malla", "Asignatura ajena a tu malla.")
            if not allowed[sid]["seleccionable"]:
                return auth.error(
                    422,
                    "asignatura_bloqueada",
                    allowed[sid]["nombre"]
                    + ": "
                    + allowed[sid]["motivos"][0]["mensaje"],
                )
        # Ninguna escritura de solicitud ocurre antes de completar validaciones.
        pid = (
            principal["id"]
            if principal
            else conn.execute(
                insert(m.solicitud).values(estudiante_id=student, periodo_id=period_id)
            ).inserted_primary_key[0]
        )
        vid = conn.execute(
            insert(m.version_solicitud).values(
                solicitud_id=pid,
                estudiante_id=student,
                numero=number + 1,
                revision_perfil_id=revision["id"],
                version_malla_id=revision["version_malla_id"],
            )
        ).inserted_primary_key[0]
        if ids:
            conn.execute(
                insert(m.detalle_solicitud),
                [
                    dict(
                        version_id=vid,
                        version_malla_id=revision["version_malla_id"],
                        **s.model_dump(),
                    )
                    for s in body.selecciones
                ],
            )
        conn.execute(
            update(m.solicitud)
            .where(m.solicitud.c.id == pid)
            .values(version_trabajo_id=vid, revision_control=number + 1)
        )
        conn.execute(
            update(m.sesion)
            .where(m.sesion.c.id == session["id"])
            .values(ultimo_en=auth.now())
        )
        principal = (
            conn.execute(select(m.solicitud).where(m.solicitud.c.id == pid))
            .mappings()
            .one()
        )
        return response(data(conn, principal))
