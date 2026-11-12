"""H07: historial en MySQL, fixtures transaccionales sin borrar históricos."""

from datetime import timedelta

import pytest
import test_auth
from fastapi.testclient import TestClient
from sqlalchemy import insert, select, update
from test_auth import pytestmark  # noqa: F401
from test_drafts import body, path
from test_submit import prepare, send

from app import auth
from app.db import models as m
from app.main import app

_identity_fixture = pytest.fixture(name="identity")(test_auth.identity.__wrapped__)
ROOT = "/api/v1/me/request-history"


def test_versions_priorities_pagination_and_login(identity, monkeypatch):
    client, conn, pid, ids, payload = prepare(identity)
    sent = send(client, pid, payload).json()
    original = client.get(ROOT).json()
    sid = sent["id"]
    endpoint = f"{ROOT}/{sid}/versions"
    old = client.get(f"{endpoint}/{sent['vigente']['id']}").json()
    assert old["version"]["vigente"]
    assert old["version"]["enviado_en"]
    assert old["selecciones"][0]["prioridad"] == "media"
    assert original["items"][0]["creado_en"]
    work = client.put(path(pid) + "/draft", json=body(ids[:1], ["alta"], 2)).json()
    listing = client.get(ROOT).json()["items"][0]
    assert listing["version_trabajo_id"] == work["trabajo"]["id"]
    assert listing["version_vigente_id"] == sent["vigente"]["id"]
    assert listing["version"]["tipo"] == "borrador"
    send(
        client,
        pid,
        dict(
            revision_esperada=3,
            revision_perfil=1,
            version_trabajo_id=work["trabajo"]["id"],
        ),
    )
    versions = client.get(endpoint + "?limit=1").json()
    assert versions["total"] == 4 and len(versions["items"]) == 1
    assert versions["items"][0]["vigente"]
    assert (
        client.get(endpoint + "?offset=1&limit=1").json()["items"][0]["tipo"]
        == "borrador"
    )
    historical = client.get(f"{endpoint}/{sent['vigente']['id']}").json()
    assert historical["version"]["estado"] == "sustituida"
    assert historical["selecciones"] == old["selecciones"]
    # El fundamento enviado protege nombre y semestre frente al catálogo actual.
    conn.execute(
        update(m.malla_asignatura)
        .where(m.malla_asignatura.c.id == ids[0])
        .values(nombre_publicado="DEMO ALTERADA", semestre_curricular=8)
    )
    assert (
        client.get(f"{endpoint}/{sent['vigente']['id']}").json()["selecciones"]
        == old["selecciones"]
    )
    before = client.get(ROOT).json()
    assert client.post("/api/v1/auth/logout").status_code == 204
    assert client.get(ROOT).status_code == 401
    later = auth.now() + timedelta(seconds=61)
    monkeypatch.setattr(auth, "now", lambda: later)
    assert (
        test_auth.verify(client, *test_auth.issue(client, identity[2])).status_code
        == 200
    )
    assert client.get(ROOT).json() == before
    assert client.get(endpoint + "?limit=51").status_code == 422
    assert client.get(ROOT + "?offset=-1").status_code == 422


def test_isolation_periods_and_foreign_version(identity):
    client, conn, pid, ids, payload = prepare(identity)
    sent = send(client, pid, payload).json()
    sid, vid = sent["id"], sent["vigente"]["id"]
    other = TestClient(app, headers=test_auth.ORIGIN)
    assert TestClient(app).get(ROOT).status_code == 401
    assert TestClient(app).get(f"{ROOT}/{sid}/versions/{vid}").status_code == 401
    test_auth.verify(
        other,
        *test_auth.issue(other, identity[2], "h07-other@estudiantes.example.test"),
    )
    assert other.get(ROOT).json()["items"] == []
    for url in (f"{ROOT}/{sid}/versions", f"{ROOT}/{sid}/versions/{vid}"):
        assert other.get(url).status_code == 404
    period = dict(
        conn.execute(select(m.periodo_academico).where(m.periodo_academico.c.id == pid))
        .mappings()
        .one()
    )
    period.pop("id")
    period["identificador"] = "DEMO-H07-OTRO"
    period["inicio_periodo"] += timedelta(days=100)
    second = conn.execute(
        insert(m.periodo_academico).values(**period)
    ).inserted_primary_key[0]
    work = client.put(path(second) + "/draft", json=body(ids[:1])).json()
    rows = client.get(ROOT).json()
    assert rows["total"] == 2
    assert rows["items"][0]["periodo_id"] == second
    assert (
        client.get(ROOT + "?limit=1&offset=1").json()["items"][0]["periodo_id"] == pid
    )
    assert client.get(f"{ROOT}/{work['id']}/versions/{vid}").status_code == 404
    # Consultable aun si el período ya no se publica para captura.
    conn.execute(
        update(m.periodo_academico)
        .where(m.periodo_academico.c.id == pid)
        .values(estado_configuracion="borrador")
    )
    assert client.get(f"{ROOT}/{sid}/versions/{vid}").status_code == 200


def test_invalidated_and_renewed_versions(identity):
    client, conn, pid, ids, payload = prepare(identity)
    sent = send(client, pid, payload).json()
    profile = client.get("/api/v1/me/academic-profile").json()
    data = dict(
        revision_esperada=1,
        malla_id=profile["malla_id"],
        semestre_declarado=2,
        estados=profile["estados"],
    )
    assert client.put("/api/v1/me/academic-profile", json=data).status_code == 200
    endpoint = f"{ROOT}/{sent['id']}/versions"
    renewed = client.get(endpoint).json()["items"][0]
    assert renewed["tipo"] == "enviada" and renewed["vigente"]
    assert renewed["enviado_en"] is None  # Renovación no inventa un nuevo envío.
    data.update(revision_esperada=2, estados=[])
    assert client.put("/api/v1/me/academic-profile", json=data).status_code == 200
    invalid = client.get(f"{endpoint}/{renewed['id']}").json()
    assert invalid["version"]["estado"] == "invalidada"
    assert not invalid["version"]["vigente"]
    assert invalid["solicitud"]["estado"] == "invalidada"
