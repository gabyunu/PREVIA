"""Integración sobre MySQL migrado; cambios de prueba siempre en rollback."""

import os

import pytest
from sqlalchemy import func, insert, select, update
from sqlalchemy.exc import IntegrityError, OperationalError

from app.db import models as m
from app.db.seed import load_pilot
from app.db.session import make_engine

pytestmark = pytest.mark.skipif(
    os.environ.get("PREVIA_TEST_MYSQL") != "1",
    reason="Requiere MySQL migrado y PREVIA_TEST_MYSQL=1",
)


@pytest.fixture
def conn():
    engine = make_engine()
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            load_pilot(connection)
            yield connection
        finally:
            transaction.rollback()
    engine.dispose()


def rejected(conn, statement):
    savepoint = conn.begin_nested()
    try:
        with pytest.raises((IntegrityError, OperationalError)):
            conn.execute(statement)
    finally:
        savepoint.rollback()


def test_seed_idempotent_and_pending(conn):
    before = {
        t.name: conn.scalar(select(func.count()).select_from(t))
        for t in m.Base.metadata.sorted_tables
    }
    assert load_pilot(conn) == {
        "asignaturas": 53,
        "prerrequisitos": 34,
        "reglas_pendientes": 18,
    }
    after = {
        t.name: conn.scalar(select(func.count()).select_from(t))
        for t in m.Base.metadata.sorted_tables
    }
    assert before == after
    assert conn.scalar(select(func.count()).select_from(m.asignatura)) == 53
    entries = conn.execute(select(m.malla_asignatura)).mappings().all()
    assert len(entries) == 53
    assert {e["semestre_curricular"] for e in entries} == set(range(1, 11))
    assert all(e["codigo_publicado"] is None for e in entries)
    english = next(e for e in entries if e["nombre_publicado"] == "Inglés III")
    assert english["revision_pendiente"] and english["condiciones_externas"]
    assert sum(e["estado_regla"] == "ninguno_explicito_propuesto" for e in entries) == 4
    assert sum(e["revision_pendiente"] for e in entries) == 18


def test_catalog_constraints(conn):
    subject = conn.execute(select(m.asignatura)).mappings().first()
    entry = conn.execute(select(m.malla_asignatura)).mappings().first()
    rejected(
        conn,
        insert(m.asignatura).values(
            identificador_catalogo=subject["identificador_catalogo"], nombre="Duplicada"
        ),
    )
    rejected(
        conn,
        insert(m.version_malla).values(carrera_id=-1, codigo_version="inexistente"),
    )
    rejected(
        conn,
        update(m.malla_asignatura)
        .where(m.malla_asignatura.c.id == entry["id"])
        .values(semestre_curricular=0),
    )
    rejected(
        conn,
        insert(m.prerrequisito).values(
            version_malla_id=entry["version_malla_id"],
            asignatura_id=entry["asignatura_id"],
            requisito_asignatura_id=entry["asignatura_id"],
        ),
    )
    rejected(
        conn,
        insert(m.prerrequisito).values(
            version_malla_id=entry["version_malla_id"],
            asignatura_id=entry["asignatura_id"],
            requisito_asignatura_id=-1,
        ),
    )
    rejected(conn, m.asignatura.delete().where(m.asignatura.c.id == subject["id"]))
    edge = conn.execute(select(m.prerrequisito)).mappings().first()
    rejected(conn, insert(m.prerrequisito).values(**dict(edge)))


def test_profile_cross_curriculum_and_states(conn):
    user_id = conn.execute(
        insert(m.usuario).values(correo_normalizado="h02-test@example.invalid")
    ).inserted_primary_key[0]
    rejected(
        conn, insert(m.usuario).values(correo_normalizado="h02-test@example.invalid")
    )
    student = conn.execute(
        insert(m.perfil_estudiante).values(usuario_id=user_id)
    ).inserted_primary_key[0]
    rejected(conn, insert(m.perfil_estudiante).values(usuario_id=user_id))
    entry = conn.execute(select(m.malla_asignatura)).mappings().first()
    revision = dict(
        estudiante_id=student,
        numero=1,
        version_malla_id=entry["version_malla_id"],
        semestre_declarado=1,
    )
    rev_id = conn.execute(
        insert(m.revision_perfil).values(**revision)
    ).inserted_primary_key[0]
    rejected(conn, insert(m.revision_perfil).values(**revision))
    declared = dict(
        revision_perfil_id=rev_id,
        malla_asignatura_id=entry["id"],
        version_malla_id=entry["version_malla_id"],
    )
    assert (
        conn.scalar(
            select(func.count())
            .select_from(m.estado_academico_declarado)
            .where(m.estado_academico_declarado.c.revision_perfil_id == rev_id)
        )
        == 0
    )
    rejected(
        conn,
        insert(m.estado_academico_declarado).values(**declared, estado="desconocido"),
    )
    for state in ("aprobada", "reprobada", "no_cursada"):
        savepoint = conn.begin_nested()
        conn.execute(
            insert(m.estado_academico_declarado).values(**declared, estado=state)
        )
        rejected(
            conn, insert(m.estado_academico_declarado).values(**declared, estado=state)
        )
        savepoint.rollback()
    career = conn.scalar(select(m.carrera.c.id))
    other = conn.execute(
        insert(m.version_malla).values(
            carrera_id=career, codigo_version="demo-prueba-otra-malla"
        )
    ).inserted_primary_key[0]
    other_entry = conn.execute(
        insert(m.malla_asignatura).values(
            version_malla_id=other,
            asignatura_id=entry["asignatura_id"],
            semestre_curricular=1,
            nombre_publicado="Demostración",
            estado_regla="requisito_no_definido",
            revision_pendiente=True,
            prerrequisito_texto_original="Pendiente",
            condiciones_externas=[],
        )
    ).inserted_primary_key[0]
    # No existe revisión de la otra malla.
    rejected(
        conn,
        insert(m.estado_academico_declarado).values(
            revision_perfil_id=rev_id,
            malla_asignatura_id=other_entry,
            version_malla_id=other,
            estado="aprobada",
        ),
    )
    # Tampoco permite disfrazar una entrada ajena con la versión de la revisión.
    rejected(
        conn,
        insert(m.estado_academico_declarado).values(
            revision_perfil_id=rev_id,
            malla_asignatura_id=other_entry,
            version_malla_id=entry["version_malla_id"],
            estado="aprobada",
        ),
    )


def test_seed_refuses_changed_data(conn):
    subject = conn.scalar(select(m.asignatura.c.id))
    conn.execute(
        update(m.asignatura)
        .where(m.asignatura.c.id == subject)
        .values(nombre="Contenido divergente de prueba")
    )
    with pytest.raises(ValueError, match="divergente"):
        load_pilot(conn)
