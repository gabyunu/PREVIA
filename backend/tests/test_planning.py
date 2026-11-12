"""H02-C sobre MySQL real; fixtures sintéticos y rollback en cada prueba."""

from datetime import datetime

import pytest
import test_persistence as persistence
from sqlalchemy import func, insert, select, update

from app.db import models as m

# Reutiliza la conexión transaccional y la condición de integración existente.
conn = persistence.conn
pytestmark = persistence.pytestmark
rejected = persistence.rejected


def period(conn, code="DEMO-H02-C", **changes):
    values = dict(
        identificador=code,
        inicio_periodo=datetime(2030, 4, 1),
        captura_desde=datetime(2030, 2, 1),
        captura_hasta=datetime(2030, 3, 1),
        zona_horaria="America/Guayaquil",
    )
    values.update(changes)
    return conn.execute(
        insert(m.periodo_academico).values(**values)
    ).inserted_primary_key[0]


@pytest.mark.parametrize(
    "changes",
    [
        {"captura_hasta": datetime(2030, 2, 1)},
        {"captura_desde": datetime(2030, 3, 2)},
        {"inicio_periodo": datetime(2030, 3, 1)},
        {"inicio_periodo": datetime(2030, 2, 28)},
        {"inicio_periodo": None, "estado_configuracion": "publicado"},
        {"estado_configuracion": "abierto"},
        {"revision_control": 0},
    ],
)
def test_invalid_period(conn, changes):
    savepoint = conn.begin_nested()
    from sqlalchemy.exc import IntegrityError, OperationalError

    try:
        with pytest.raises((IntegrityError, OperationalError)):
            period(conn, **changes)
    finally:
        savepoint.rollback()


def test_period_identifier_and_draft(conn):
    p = period(conn, inicio_periodo=None)
    rejected(
        conn,
        insert(m.periodo_academico).values(
            identificador="DEMO-H02-C",
            captura_desde=datetime(2030, 2, 1),
            captura_hasta=datetime(2030, 3, 1),
            zona_horaria="UTC",
        ),
    )
    rejected(
        conn,
        update(m.periodo_academico)
        .where(m.periodo_academico.c.id == p)
        .values(estado_configuracion="publicado"),
    )
    conn.execute(
        update(m.periodo_academico)
        .where(m.periodo_academico.c.id == p)
        .values(inicio_periodo=datetime(2030, 4, 1), estado_configuracion="publicado")
    )


def test_capacity_unknown_zero_unique_and_foreign_keys(conn):
    p = period(conn)
    entry = conn.execute(select(m.malla_asignatura)).mappings().first()
    values = dict(malla_asignatura_id=entry["id"], periodo_id=p)
    assert conn.scalar(select(func.count()).select_from(m.planificacion_cupos)) == 0
    plan = conn.execute(
        insert(m.planificacion_cupos).values(**values)
    ).inserted_primary_key[0]
    query = select(m.planificacion_cupos).where(m.planificacion_cupos.c.id == plan)
    assert conn.execute(query).mappings().one()["cupos_planificados"] is None
    # Hace observable la actualización de fecha sin esperas de reloj.
    conn.execute(
        update(m.planificacion_cupos)
        .where(m.planificacion_cupos.c.id == plan)
        .values(actualizado_en=datetime(2000, 1, 1))
    )
    conn.execute(
        update(m.planificacion_cupos)
        .where(m.planificacion_cupos.c.id == plan)
        .values(cupos_planificados=0)
    )
    row = conn.execute(query).mappings().one()
    assert row["cupos_planificados"] == 0
    assert row["actualizado_en"] > datetime(2000, 1, 1)
    rejected(conn, insert(m.planificacion_cupos).values(**values))
    rejected(
        conn,
        update(m.planificacion_cupos)
        .where(m.planificacion_cupos.c.id == plan)
        .values(cupos_planificados=-1),
    )
    for bad in ({"periodo_id": -1}, {"malla_asignatura_id": -1}):
        rejected(conn, insert(m.planificacion_cupos).values(**(values | bad)))
    rejected(
        conn,
        update(m.planificacion_cupos)
        .where(m.planificacion_cupos.c.id == plan)
        .values(responsable_usuario_id=-1),
    )
    rejected(conn, m.periodo_academico.delete().where(m.periodo_academico.c.id == p))
    rejected(
        conn, m.malla_asignatura.delete().where(m.malla_asignatura.c.id == entry["id"])
    )
    # La misma identidad de catálogo en otra versión conserva planificación propia.
    other = conn.execute(
        insert(m.version_malla).values(
            carrera_id=conn.scalar(select(m.carrera.c.id)),
            codigo_version="DEMO-H02-C-OTRA",
        )
    ).inserted_primary_key[0]
    data = {k: v for k, v in entry.items() if k != "id"} | {"version_malla_id": other}
    other_entry = conn.execute(
        insert(m.malla_asignatura).values(**data)
    ).inserted_primary_key[0]
    conn.execute(
        insert(m.planificacion_cupos).values(
            periodo_id=p, malla_asignatura_id=other_entry, cupos_planificados=20
        )
    )
    conn.execute(
        insert(m.planificacion_cupos).values(
            **(values | {"periodo_id": period(conn, code="DEMO-H02-C-OTRO")})
        )
    )


def test_notes_and_metadata(conn):
    p = period(conn)
    entry = conn.scalar(select(m.malla_asignatura.c.id))
    author = conn.execute(
        insert(m.usuario).values(correo_normalizado="notas-h02c@example.invalid")
    ).inserted_primary_key[0]
    plan = conn.execute(
        insert(m.planificacion_cupos).values(
            periodo_id=p, malla_asignatura_id=entry, responsable_usuario_id=author
        )
    ).inserted_primary_key[0]
    note = dict(
        planificacion_id=plan,
        autor_usuario_id=author,
        tipo="observacion",
        contenido="Nota sintética de prueba",
    )
    for kind in ("observacion", "propuesta", "decision"):
        conn.execute(insert(m.nota_administrativa).values(**(note | {"tipo": kind})))
    for bad in (
        {"planificacion_id": -1},
        {"autor_usuario_id": -1},
        {"tipo": "otro"},
        {"contenido": "  "},
    ):
        rejected(conn, insert(m.nota_administrativa).values(**(note | bad)))
    rejected(
        conn, m.planificacion_cupos.delete().where(m.planificacion_cupos.c.id == plan)
    )
    rejected(conn, m.usuario.delete().where(m.usuario.c.id == author))
    # Las FK de usuario no conceden roles; autorización pendiente de servicio admin.
    assert (
        conn.scalar(
            select(func.count())
            .select_from(m.usuario_rol)
            .where(m.usuario_rol.c.usuario_id == author)
        )
        == 0
    )
    conn.execute(
        update(m.malla_asignatura)
        .where(m.malla_asignatura.c.id == entry)
        .values(
            fuente_regla="DEMO: revisión sintética",
            regla_revisada_en=datetime(2030, 1, 1),
        )
    )
    assert (
        conn.scalar(
            select(m.malla_asignatura.c.fuente_regla).where(
                m.malla_asignatura.c.id == entry
            )
        )
        == "DEMO: revisión sintética"
    )
