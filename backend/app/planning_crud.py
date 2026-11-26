"""Native Flask-SQLAlchemy CRUD for planned seats (administrator only).

CRUD is deliberately limited to planning records. Immutable student submissions,
security/audit events, and historical versions cannot be physically deleted.
"""

from __future__ import annotations

import hmac
from datetime import UTC, datetime

from flask import Blueprint, jsonify, request
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from app import auth
from app.db import models as m
from app.flask_api import db

planning_api = Blueprint("planning", __name__, url_prefix="/api/v1/admin/planning")


class PlannedCapacity(db.Model):
    __table__ = m.planificacion_cupos


class NewCapacity(BaseModel):
    model_config = ConfigDict(extra="forbid")
    periodo_id: int = Field(strict=True, gt=0)
    malla_asignatura_id: int = Field(strict=True, gt=0)
    cupos_planificados: int | None = Field(ge=0, le=1_000_000, strict=True)


class CapacityUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cupos_planificados: int | None = Field(ge=0, le=1_000_000, strict=True)


def failure(status, code, message):
    return jsonify(error={"codigo": code, "mensaje": message}), status


def authorized(*, writing=False):
    """Return an HTTP response on failure; otherwise return None."""
    conn = db.session.connection()
    identity = auth.current(conn, request)
    if identity is None:
        return failure(401, "sesion_requerida", "Inicia sesión para continuar.")
    session, user = identity
    if "administrador" not in auth.user_data(conn, user)["roles"]:
        return failure(403, "permiso_requerido", "Se requiere el rol administrador.")
    if writing:
        if not auth.origin_ok(request):
            return failure(403, "origen_invalido", "Origen no autorizado.")
        if not hmac.compare_digest(
            session["csrf_digest"],
            auth.digest(request.headers.get("X-CSRF-Token", "")),
        ):
            return failure(403, "csrf_invalido", "No se pudo validar la petición.")
    conn.execute(
        update(m.sesion)
        .where(m.sesion.c.id == session["id"])
        .values(ultimo_en=auth.now())
    )
    return None


def serialize(item):
    return {
        "id": item.id,
        "periodo_id": item.periodo_id,
        "malla_asignatura_id": item.malla_asignatura_id,
        "cupos_planificados": item.cupos_planificados,
        "actualizado_en": item.actualizado_en.isoformat() + "Z" if item.actualizado_en else None,
        "responsable_usuario_id": item.responsable_usuario_id,
    }


def validated(model):
    if not request.is_json:
        return None
    obj = request.get_json(silent=True)
    if not isinstance(obj, dict):
        return None
    try:
        return model.model_validate(obj)
    except ValidationError:
        return None


@planning_api.get("")
def list_planning():
    denied = authorized()
    if denied is not None:
        db.session.rollback()
        return denied
    raw = request.args.get("periodo_id")
    if raw is not None and (not raw.isdecimal() or int(raw) < 1):
        db.session.rollback()
        return failure(422, "entrada_invalida", "Período inválido.")
    statement = select(PlannedCapacity).order_by(PlannedCapacity.id).limit(500)
    if raw:
        statement = statement.where(PlannedCapacity.periodo_id == int(raw))
    items = db.session.scalars(statement).all()
    result = [serialize(item) for item in items]
    db.session.commit()  # Record session activity, even for reads.
    return jsonify(items=result, total=len(result), limite=500)


@planning_api.get("/<int:item_id>")
def get_planning(item_id):
    denied = authorized()
    if denied is not None:
        db.session.rollback()
        return denied
    item = db.session.get(PlannedCapacity, item_id)
    if item is None:
        db.session.rollback()
        return failure(404, "no_encontrado", "Registro no encontrado.")
    result = serialize(item)
    db.session.commit()
    return jsonify(result)


@planning_api.post("")
def create_planning():
    denied = authorized(writing=True)
    if denied is not None:
        db.session.rollback()
        return denied
    body = validated(NewCapacity)
    if body is None:
        db.session.rollback()
        return failure(422, "entrada_invalida", "Revisa los campos del registro.")

    # Protect against nonexistent IDs, including when the DB uses a test fixture.
    period_exists = db.session.scalar(select(m.periodo_academico.c.id).where(m.periodo_academico.c.id == body.periodo_id))
    subject_exists = db.session.scalar(select(m.malla_asignatura.c.id).where(m.malla_asignatura.c.id == body.malla_asignatura_id))
    if not period_exists or not subject_exists:
        db.session.rollback()
        return failure(422, "referencia_invalida", "El período o la asignatura no existen.")
    identity = auth.current(db.session.connection(), request)
    record = PlannedCapacity(
        periodo_id=body.periodo_id,
        malla_asignatura_id=body.malla_asignatura_id,
        cupos_planificados=body.cupos_planificados,
        responsable_usuario_id=identity[1]["id"],
        actualizado_en=auth.now(),
    )
    db.session.add(record)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return failure(409, "registro_duplicado", "Ya existe una planificación para esa asignatura y período.")
    return jsonify(serialize(record)), 201


@planning_api.put("/<int:item_id>")
def update_planning(item_id):
    denied = authorized(writing=True)
    if denied is not None:
        db.session.rollback()
        return denied
    body = validated(CapacityUpdate)
    if body is None:
        db.session.rollback()
        return failure(422, "entrada_invalida", "Revisa los campos del registro.")
    record = db.session.get(PlannedCapacity, item_id)
    if record is None:
        db.session.rollback()
        return failure(404, "no_encontrado", "Registro no encontrado.")
    record.cupos_planificados = body.cupos_planificados
    record.actualizado_en = auth.now()
    identity = auth.current(db.session.connection(), request)
    record.responsable_usuario_id = identity[1]["id"]
    db.session.commit()
    return jsonify(serialize(record))


@planning_api.delete("/<int:item_id>")
def delete_planning(item_id):
    denied = authorized(writing=True)
    if denied is not None:
        db.session.rollback()
        return denied
    record = db.session.get(PlannedCapacity, item_id)
    if record is None:
        db.session.rollback()
        return failure(404, "no_encontrado", "Registro no encontrado.")
    db.session.delete(record)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return failure(409, "registro_relacionado", "No se puede eliminar una planificación con notas asociadas.")
    return "", 204


@planning_api.get("/catalog")
def catalog():
    denied = authorized()
    if denied is not None:
        db.session.rollback()
        return denied
    periods = db.session.execute(
        select(m.periodo_academico.c.id, m.periodo_academico.c.identificador)
        .order_by(m.periodo_academico.c.id)
    ).mappings().all()
    subjects = db.session.execute(
        select(
            m.malla_asignatura.c.id,
            m.malla_asignatura.c.codigo_publicado,
            m.malla_asignatura.c.nombre_publicado,
            m.malla_asignatura.c.semestre_curricular,
        ).order_by(m.malla_asignatura.c.semestre_curricular, m.malla_asignatura.c.nombre_publicado)
    ).mappings().all()
    data = {"periodos": [dict(p) for p in periods], "asignaturas": [dict(s) for s in subjects]}
    db.session.commit()
    return jsonify(data)
