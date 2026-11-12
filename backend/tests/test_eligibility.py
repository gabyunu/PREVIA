"""H04-B: API y reglas sobre MySQL local, con rollback por caso."""

import pytest
import test_auth
from fastapi.testclient import TestClient
from sqlalchemy import insert, select, update
from test_academic import PATH, login
from test_auth import ORIGIN, issue, pytestmark, verify  # noqa: F401

from app.db import models as m
from app.main import app

_identity_fixture = pytest.fixture(name="identity")(test_auth.identity.__wrapped__)
ELIGIBILITY = "/api/v1/me/eligibility"


def rows(client):
    response = client.get(ELIGIBILITY)
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    data = response.json()
    assert data["base_datos"] == "AUTODECLARADA"
    assert data["provisional"]
    return {r["nombre"]: r for r in data["materias"]}


def test_authentication_and_missing_profile(identity):
    client = identity[0]
    assert client.get(ELIGIBILITY).status_code == 401
    login(identity)
    assert client.get(ELIGIBILITY).json()["error"]["codigo"] == "perfil_requerido"


def test_prerequisites_repetition_and_latest_revision(identity):
    client, conn, body, subjects = login(identity)
    ids = {s["nombre_publicado"]: s["malla_asignatura_id"] for s in subjects}
    states = {name: "no_cursada" for name in ids}
    states.update(
        {
            "Cálculo I": "aprobada",
            "Álgebra Lineal": "aprobada",
            "Química I": "reprobada",
        }
    )

    def save():
        body["estados"] = [
            dict(malla_asignatura_id=ids[n], estado=s) for n, s in states.items()
        ]
        response = client.put(PATH, json=body)
        assert response.status_code == 200
        body["revision_esperada"] = response.json()["revision"]

    save()
    result = rows(client)
    assert len(result) == 53
    assert result["Cálculo II"]["seleccionable"]
    assert result["Física I"]["seleccionable"]
    assert not result["Probabilidad y Estadística"]["seleccionable"]
    assert not result["Química II"]["seleccionable"]
    assert result["Química I"]["seleccionable"]  # repetición, ninguno explícito
    assert not result["Cálculo I"]["seleccionable"]
    assert result["Cálculo I"]["motivos"][0]["codigo"] == "ya_aprobada"
    assert result["Biología I"]["seleccionable"]
    assert (
        len(result["Introducción a la Programación"]["prerrequisitos_aprobados"]) == 2
    )
    assert (
        result["Química II"]["prerrequisitos_pendientes"][0]["estado_declarado"]
        == "reprobada"
    )
    assert not result["Inglés III"]["seleccionable"]
    assert result["Inglés III"]["advertencia"]
    for row in result.values():
        if row["advertencia"]:
            assert not row["seleccionable"]
    # AND: uno de dos aprobado no basta; ausencia nunca satisface requisito.
    states.pop("Álgebra Lineal")
    states["Cálculo II"] = "aprobada"
    states["Introducción a la Programación"] = "reprobada"
    save()
    result = rows(client)
    assert not result["Introducción a la Programación"]["seleccionable"]
    assert (
        result["Introducción a la Programación"]["prerrequisitos_pendientes"][0][
            "estado_declarado"
        ]
        is None
    )
    assert not result["Probabilidad y Estadística"]["seleccionable"]
    states["Álgebra Lineal"] = "aprobada"
    save()
    assert rows(client)["Introducción a la Programación"]["seleccionable"]
    assert rows(client)["Probabilidad y Estadística"]["seleccionable"]
    assert client.get(ELIGIBILITY).json()["revision_perfil"] == 3
    assert len(conn.execute(select(m.revision_perfil)).all()) == 3


@pytest.mark.parametrize(
    "rule,review,external",
    [
        ("ninguno_identificado_sin_confirmar", False, []),
        ("ninguno_explicito_propuesto", True, []),
        ("ninguno_explicito_propuesto", False, ["Condición sintética no comprobable"]),
        ("prerrequisitos_asignaturas_propuestos", False, []),
    ],
)
def test_unknown_rules_never_enable(identity, rule, review, external):
    client, conn, body, subjects = login(identity)
    subject = subjects[0]
    body["estados"] = [
        dict(malla_asignatura_id=subject["malla_asignatura_id"], estado="no_cursada")
    ]
    assert client.put(PATH, json=body).status_code == 200
    # Solo fixture transaccional: no cambia el catálogo persistido.
    conn.execute(
        update(m.malla_asignatura)
        .where(m.malla_asignatura.c.id == subject["malla_asignatura_id"])
        .values(
            estado_regla=rule, revision_pendiente=review, condiciones_externas=external
        )
    )
    row = rows(client)[subject["nombre_publicado"]]
    assert not row["seleccionable"]
    assert row["advertencia"]


def test_students_and_curriculum_versions_isolated(identity):
    client, conn, body, subjects = login(identity)
    body["estados"] = [
        dict(malla_asignatura_id=s["malla_asignatura_id"], estado="no_cursada")
        for s in subjects
    ]
    assert client.put(PATH, json=body).status_code == 200
    other = TestClient(app, headers=ORIGIN)
    result = verify(
        other, *issue(other, identity[2], "h04b-otro@estudiantes.example.test")
    )
    other.headers["X-CSRF-Token"] = result.json()["csrf_token"]
    assert other.get(ELIGIBILITY).status_code == 409
    other_body = dict(
        body, estados=[dict(s, estado="aprobada") for s in body["estados"]]
    )
    assert other.put(PATH, json=other_body).status_code == 200
    assert rows(client)["Cálculo I"]["seleccionable"]
    assert not rows(other)["Cálculo I"]["seleccionable"]
    career = conn.execute(
        insert(m.carrera).values(codigo="FIXTURE-H04B", nombre="Fixture sintético")
    ).inserted_primary_key[0]
    version = conn.execute(
        insert(m.version_malla).values(carrera_id=career, codigo_version="fixture-h04b")
    ).inserted_primary_key[0]
    originals = (
        conn.execute(
            select(m.malla_asignatura)
            .where(m.malla_asignatura.c.version_malla_id == body["malla_id"])
            .limit(2)
        )
        .mappings()
        .all()
    )
    copies = []
    for original in originals:
        values = dict(original)
        values.pop("id")
        values.update(version_malla_id=version)
        copies.append(
            conn.execute(
                insert(m.malla_asignatura).values(**values)
            ).inserted_primary_key[0]
        )
    conn.execute(
        insert(m.prerrequisito).values(
            version_malla_id=version,
            asignatura_id=originals[0]["asignatura_id"],
            requisito_asignatura_id=originals[1]["asignatura_id"],
        )
    )
    assert len(rows(client)) == 53
    assert rows(client)["Cálculo I"]["seleccionable"]
    # Un perfil de otra versión se evalúa en esa versión, sin heredar aprobaciones.
    student = conn.scalar(
        select(m.perfil_estudiante.c.id).where(
            m.perfil_estudiante.c.usuario_id == client.get("/api/v1/me").json()["id"]
        )
    )
    revision = conn.execute(
        insert(m.revision_perfil).values(
            estudiante_id=student,
            numero=2,
            version_malla_id=version,
            semestre_declarado=1,
        )
    ).inserted_primary_key[0]
    conn.execute(
        insert(m.estado_academico_declarado).values(
            revision_perfil_id=revision,
            version_malla_id=version,
            malla_asignatura_id=copies[0],
            estado="no_cursada",
        )
    )
    result = rows(client)
    assert len(result) == 2
    row = result[originals[0]["nombre_publicado"]]
    assert not row["seleccionable"]
    assert row["prerrequisitos_pendientes"][0]["estado_declarado"] is None


@pytest.mark.parametrize("declared_state", ["no_cursada", "reprobada"])
def test_candidate_undeclared_despite_passed_prerequisites(identity, declared_state):
    client, _, body, subjects = login(identity)
    ids = {s["nombre_publicado"]: s["malla_asignatura_id"] for s in subjects}
    body["estados"] = [dict(malla_asignatura_id=ids["Cálculo I"], estado="aprobada")]
    assert client.put(PATH, json=body).status_code == 200
    row = rows(client)["Cálculo II"]
    assert row["estado_declarado"] is None
    assert row["prerrequisitos_cumplidos"]
    assert len(row["prerrequisitos_aprobados"]) == 1
    assert row["prerrequisitos_pendientes"] == []
    assert not row["seleccionable"]
    assert row["motivos"] == [
        dict(
            codigo="declaracion_incompleta",
            mensaje="Declara el estado académico de esta asignatura.",
        )
    ]
    body["revision_esperada"] = 1
    body["estados"].append(
        dict(malla_asignatura_id=ids["Cálculo II"], estado=declared_state)
    )
    assert client.put(PATH, json=body).status_code == 200
    row = rows(client)["Cálculo II"]
    assert row["prerrequisitos_cumplidos"]
    assert row["seleccionable"]
    assert row["motivos"] == []
