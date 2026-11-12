"""H04-A sobre MySQL; cada caso revierte sus escrituras."""

from datetime import timedelta

import pytest
import test_auth
from fastapi.testclient import TestClient
from sqlalchemy import func, insert, select
from test_auth import ORIGIN, issue, pytestmark, verify  # noqa: F401

from app import academic
from app.db import models as m
from app.main import app

_identity_fixture = pytest.fixture(name="identity")(test_auth.identity.__wrapped__)

PATH = "/api/v1/me/academic-profile"


def login(identity):
    client, conn, messages, _ = identity
    result = verify(client, *issue(client, messages))
    client.headers["X-CSRF-Token"] = result.json()["csrf_token"]
    version = client.get("/api/v1/curricula").json()[0]
    subjects = client.get("/api/v1/curricula/" + str(version["id"])).json()[
        "asignaturas"
    ]
    body = dict(
        revision_esperada=0,
        malla_id=version["id"],
        semestre_declarado=3,
        estados=[
            dict(malla_asignatura_id=s["malla_asignatura_id"], estado=state)
            for s, state in zip(subjects, ["aprobada", "reprobada", "no_cursada"])
        ],
    )
    return client, conn, body, subjects


def test_session_and_catalog(identity):
    client = identity[0]
    assert (
        client.put(
            PATH,
            json=dict(
                revision_esperada=0, malla_id=1, semestre_declarado=1, estados=[]
            ),
        ).status_code
        == 401
    )
    for path in [PATH, "/api/v1/careers", "/api/v1/curricula", "/api/v1/curricula/1"]:
        assert client.get(path).status_code == 401
    client, _, body, subjects = login(identity)
    assert len(subjects) == 53
    assert {s["semestre_curricular"] for s in subjects} == set(range(1, 11))
    assert client.get(PATH).json()["estados"] == []
    assert client.get(PATH).json()["revision"] == 0
    assert client.get("/api/v1/curricula/" + str(body["malla_id"])).json()[
        "provisional"
    ]
    assert len(client.get("/api/v1/careers").json()) == 1
    assert client.get("/api/v1/curricula/999999").status_code == 404


def test_revisions_reload_and_full_replacement(identity):
    client, conn, body, _ = login(identity)
    response = client.put(PATH, json=body)
    assert response.status_code == 200
    assert response.json()["revision"] == 1
    # Un cliente nuevo recupera el perfil desde MySQL usando la sesión.
    reloaded = TestClient(app, headers=ORIGIN)
    reloaded.cookies.update(client.cookies)
    assert reloaded.get(PATH).json()["estados"] == body["estados"]
    assert reloaded.get(PATH).json()["semestre_declarado"] == 3
    assert client.put(PATH, json=body).status_code == 409
    body.update(revision_esperada=1, estados=body["estados"][:1])
    assert client.put(PATH, json=body).json()["revision"] == 2
    assert len(client.get(PATH).json()["estados"]) == 1
    revisions = (
        conn.execute(select(m.revision_perfil).order_by(m.revision_perfil.c.numero))
        .mappings()
        .all()
    )
    assert len(revisions) == 2
    assert (
        conn.scalar(
            select(func.count())
            .select_from(m.estado_academico_declarado)
            .where(
                m.estado_academico_declarado.c.revision_perfil_id == revisions[0]["id"]
            )
        )
        == 3
    )
    body.update(revision_esperada=2, estados=[])
    assert client.put(PATH, json=body).json()["estados"] == []


def test_validation_atomicity_and_security(identity):
    client, conn, body, _ = login(identity)
    assert (
        client.put(PATH, json=body, headers={"X-CSRF-Token": "incorrecto"}).status_code
        == 403
    )
    assert (
        client.put(PATH, json=body, headers={"Origin": "http://evil.test"}).status_code
        == 403
    )
    for invalid in ["cursada", "APROBADA", "", None]:
        candidate = {**body, "estados": [{**body["estados"][0], "estado": invalid}]}
        assert client.put(PATH, json=candidate).status_code == 422
    duplicate = {**body, "estados": [body["estados"][0]] * 2}
    assert client.put(PATH, json=duplicate).status_code == 422
    # Entrada existente de otra malla, creada solo dentro del rollback de prueba.
    vid = conn.execute(
        insert(m.version_malla).values(
            carrera_id=conn.scalar(
                select(m.version_malla.c.carrera_id).where(
                    m.version_malla.c.id == body["malla_id"]
                )
            ),
            codigo_version="fixture-ajena-h04",
        )
    ).inserted_primary_key[0]
    original = dict(conn.execute(select(m.malla_asignatura)).mappings().first())
    original.pop("id")
    original["version_malla_id"] = vid
    foreign = conn.execute(
        insert(m.malla_asignatura).values(**original)
    ).inserted_primary_key[0]
    # No alterar la elección única del piloto durante esta prueba.
    conn.execute(
        m.version_malla.update()
        .where(m.version_malla.c.id == vid)
        .values(
            carrera_id=conn.execute(
                insert(m.carrera).values(
                    codigo="FIXTURE-H04", nombre="Fixture sintético solo en rollback"
                )
            ).inserted_primary_key[0]
        )
    )
    candidate = {
        **body,
        "estados": body["estados"]
        + [dict(malla_asignatura_id=foreign, estado="aprobada")],
    }
    assert (
        client.put(PATH, json=candidate).json()["error"]["codigo"] == "fuera_de_malla"
    )
    for key in ["estudiante_id", "usuario_id"]:
        assert client.put(PATH, json={**body, key: 999}).status_code == 422
    assert client.get(PATH).json()["revision"] == 0
    assert conn.scalar(select(func.count()).select_from(m.revision_perfil)) == 0


def test_other_user_and_relogin(identity, monkeypatch):
    client, _, body, _ = login(identity)
    first = client.get("/api/v1/me").json()["id"]
    assert client.put(PATH, json=body).status_code == 200
    messages = identity[2]
    other = TestClient(app, headers=ORIGIN)
    result = verify(other, *issue(other, messages, "otro-h04@estudiantes.example.test"))
    other.headers["X-CSRF-Token"] = result.json()["csrf_token"]
    assert other.get(PATH).json()["revision"] == 0
    assert other.put(PATH, json={**body, "usuario_id": first}).status_code == 422
    assert other.put(PATH, json=body).status_code == 200
    assert client.get(PATH).json()["revision"] == 1
    assert (
        other.put(
            "/api/v1/users/" + str(first) + "/academic-profile", json=body
        ).status_code
        == 404
    )
    assert client.post("/api/v1/auth/logout").status_code == 204
    assert client.get(PATH).status_code == 401
    later = test_auth.auth.now() + timedelta(seconds=61)
    monkeypatch.setattr(test_auth.auth, "now", lambda: later)
    reentry = TestClient(app, headers=ORIGIN)
    verify(reentry, *issue(reentry, messages, "otro-h04@estudiantes.example.test"))
    assert reentry.get(PATH).json()["estados"] == body["estados"]


def test_storage_failure_rolls_back(identity, monkeypatch):
    client, conn, body, _ = login(identity)
    real_insert = academic.insert

    def failing_insert(table):
        if table is m.estado_academico_declarado:
            raise RuntimeError("fallo de persistencia simulado")
        return real_insert(table)

    monkeypatch.setattr(academic, "insert", failing_insert)

    with pytest.raises(RuntimeError, match="fallo de persistencia"):
        client.put(PATH, json=body)
    assert client.get(PATH).json()["revision"] == 0
    assert conn.scalar(select(func.count()).select_from(m.revision_perfil)) == 0


def test_all_subjects_and_change_curriculum_rejected(identity):
    client, _, body, subjects = login(identity)
    body["estados"] = [
        dict(malla_asignatura_id=s["malla_asignatura_id"], estado="aprobada")
        for s in subjects
    ]
    assert client.put(PATH, json=body).status_code == 200
    assert len(client.get(PATH).json()["estados"]) == 53
    candidate = dict(body, revision_esperada=1, malla_id=999999)
    response = client.put(PATH, json=candidate)
    assert response.status_code == 409
    assert response.json()["error"]["codigo"] == "cambio_malla_no_habilitado"
    assert client.get(PATH).json()["revision"] == 1
    preflight = client.options(
        PATH,
        headers={
            **ORIGIN,
            "Access-Control-Request-Method": "PUT",
            "Access-Control-Request-Headers": "Content-Type,X-CSRF-Token",
        },
    )
    assert preflight.status_code == 200
