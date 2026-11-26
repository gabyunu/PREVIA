"""Self-contained Flask-SQLAlchemy CRUD checks with in-memory SQLite.

Run: python -m pytest -q tests/test_flask_final.py
Does not access or modify the persistent MySQL development database.
"""

import os
from datetime import datetime, UTC

import pytest
from sqlalchemy import event, insert

from app import auth
from app.db import models as m

# Import-time Flask factory builds a config but does not connect to the database.
os.environ.setdefault("MYSQL_USER", "test")
os.environ.setdefault("MYSQL_PASSWORD", "not_a_secret")
os.environ.setdefault("MYSQL_DATABASE", "test")
os.environ.setdefault("AUTH_HMAC_KEY", "abcdef0123456789" * 4)

from app.flask_api import create_app, db  # noqa: E402


@pytest.fixture
def client(monkeypatch):
    app = create_app("sqlite:///:memory:")
    app.config["TESTING"] = True
    with app.app_context():
        # The existing schema uses a MySQL-specific CHECK and datetime default.
        @event.listens_for(db.engine, "connect")
        def configure_sqlite(connection, _):
            connection.create_function("CHAR_LENGTH", 1, lambda x: len(x or ""))
            connection.create_function("UTC_TIMESTAMP", 0, lambda: "2026-11-22 00:00:00")
            connection.execute("PRAGMA foreign_keys=ON")

        db.create_all()
        db.session.execute(insert(m.carrera).values(id=1, codigo="TEST", nombre="Test"))
        db.session.execute(insert(m.version_malla).values(id=1, carrera_id=1, codigo_version="test", estado_publicacion="borrador", revision_control=1))
        db.session.execute(insert(m.asignatura).values(id=1, identificador_catalogo="SUBJ-1", nombre="Sample"))
        db.session.execute(insert(m.malla_asignatura).values(
            id=1, version_malla_id=1, asignatura_id=1, semestre_curricular=1,
            nombre_publicado="Sample", estado_regla="ninguno_explicito_propuesto",
            revision_pendiente=False, prerrequisito_texto_original="", condiciones_externas=[],
        ))
        db.session.execute(insert(m.periodo_academico).values(
            id=1, identificador="TEST", captura_desde=datetime(2026, 1, 1),
            captura_hasta=datetime(2026, 2, 1), zona_horaria="America/Guayaquil",
            estado_configuracion="borrador", revision_control=1,
        ))
        db.session.execute(insert(m.usuario).values(id=7, correo_normalizado="admin@estudiantes.example.test", activo=True, creado_en=datetime.now(UTC).replace(tzinfo=None)))
        db.session.commit()

        monkeypatch.setattr(auth, "current", lambda c, r: ({"id": 999, "csrf_digest": "signed"}, {"id": 7}))
        monkeypatch.setattr(auth, "user_data", lambda c, u: {"id": 7, "roles": ["administrador"]})
        monkeypatch.setattr(auth, "origin_ok", lambda r: r.headers.get("Origin") == "http://127.0.0.1:4200")
        monkeypatch.setattr(auth, "digest", lambda v: "signed" if v == "good-csrf" else "invalid")
        yield app.test_client()


HEADERS = {"Origin": "http://127.0.0.1:4200", "X-CSRF-Token": "good-csrf"}


def test_health_and_openapi(client):
    assert client.get("/health").json == {"status": "ok"}
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "post" in response.json["paths"]["/api/v1/admin/planning"]
    assert "delete" in response.json["paths"]["/api/v1/admin/planning/{item_id}"]


def test_full_crud_and_unknown_capacity(client):
    base = "/api/v1/admin/planning"
    assert client.get(base).json["items"] == []
    created = client.post(base, json={"periodo_id": 1, "malla_asignatura_id": 1, "cupos_planificados": 25}, headers=HEADERS)
    assert created.status_code == 201
    item = created.json
    assert item["cupos_planificados"] == 25
    url = base + "/" + str(item["id"])
    assert client.get(url).json["cupos_planificados"] == 25
    assert client.get(base).json["items"][0]["id"] == item["id"]
    changed = client.put(url, json={"cupos_planificados": None}, headers=HEADERS)
    assert changed.status_code == 200
    assert changed.json["cupos_planificados"] is None
    assert client.delete(url, headers=HEADERS).status_code == 204
    assert client.get(url).status_code == 404


def test_duplicate_validation_and_csrf(client):
    url = "/api/v1/admin/planning"
    data = {"periodo_id": 1, "malla_asignatura_id": 1, "cupos_planificados": 40}
    assert client.post(url, json=data, headers={"Origin": HEADERS["Origin"]}).status_code == 403
    assert client.post(url, json={**data, "cupos_planificados": -3}, headers=HEADERS).status_code == 422
    assert client.post(url, json={**data, "malla_asignatura_id": 999}, headers=HEADERS).status_code == 422
    assert client.post(url, json=data, headers=HEADERS).status_code == 201
    assert client.post(url, json=data, headers=HEADERS).status_code == 409


def test_student_cannot_access_administration(client, monkeypatch):
    monkeypatch.setattr(auth, "user_data", lambda c, u: {"id": 7, "roles": ["estudiante"]})
    assert client.get("/api/v1/admin/planning").status_code == 403
    assert client.post("/api/v1/admin/planning", json={"periodo_id": 1}, headers=HEADERS).status_code == 403


def test_role_boundaries_cannot_be_bypassed_with_direct_http(client, monkeypatch):
    # A valid administrator session must not read student-owned profiles or drafts.
    assert client.get("/api/v1/me/academic-profile").status_code == 403
    assert client.get("/api/v1/me/eligibility").status_code == 403
    assert client.get("/api/v1/me/request-history").status_code == 403

    # A student cannot read admin reports nor write CRUD records via a forged URL.
    monkeypatch.setattr(auth, "user_data", lambda c, u: {"id": 7, "roles": ["estudiante"]})
    assert client.get("/api/v1/admin/demand").status_code == 403
    assert client.get("/api/v1/admin/demand/options").status_code == 403
    assert client.get("/api/v1/admin/planning").status_code == 403
    assert client.delete("/api/v1/admin/planning/1", headers=HEADERS).status_code == 403

    # All protected endpoints require a valid session.
    monkeypatch.setattr(auth, "current", lambda c, r: None)
    assert client.get("/api/v1/admin/planning").status_code == 401
    assert client.get("/api/v1/me/academic-profile").status_code == 401


def test_demo_identity_provisioning_is_idempotent_and_never_promotes_students(client):
    from app.db.demo_accounts import STUDENT_EMAIL, ADMIN_EMAIL, provision
    with client.application.app_context():
        with db.engine.begin() as conn:
            sid = provision(conn, STUDENT_EMAIL, "estudiante")
            aid = provision(conn, ADMIN_EMAIL, "administrador")
            assert sid != aid
            assert provision(conn, STUDENT_EMAIL, "estudiante") == sid
            assert provision(conn, ADMIN_EMAIL, "administrador") == aid
            with pytest.raises(ValueError):
                provision(conn, STUDENT_EMAIL, "administrador")
            with pytest.raises(ValueError):
                provision(conn, ADMIN_EMAIL, "estudiante")
