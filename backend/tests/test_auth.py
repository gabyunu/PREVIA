"""Identidad con MySQL real; rollback salvo la prueba de concurrencia."""

import os
import re
import secrets
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import timedelta
from threading import Barrier
from urllib.request import urlopen

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, func, insert, select, update

from app import auth
from app.db import models as m
from app.db.session import make_engine
from app.main import app

pytestmark = pytest.mark.skipif(
    os.environ.get("PREVIA_TEST_MYSQL") != "1",
    reason="Requiere MySQL migrado y PREVIA_TEST_MYSQL=1",
)
ORIGIN = {"Origin": "http://127.0.0.1:4200"}
EMAIL = "h02b-prueba@estudiantes.example.test"


@pytest.fixture
def identity(monkeypatch):
    engine = make_engine()
    with engine.connect() as conn:
        transaction = conn.begin()

        class TestEngine:
            @contextmanager
            def begin(self):
                with conn.begin_nested():
                    yield conn

        monkeypatch.setattr(auth, "engine", lambda: TestEngine())
        monkeypatch.setattr(auth, "settings", lambda: config)
        config = auth.Settings()
        messages = []
        monkeypatch.setattr(
            auth, "send_code", lambda email, code: messages.append((email, code))
        )
        client = TestClient(app, headers=ORIGIN)
        try:
            yield client, conn, messages, config
        finally:
            transaction.rollback()
    engine.dispose()


def issue(client, messages, email=EMAIL):
    response = client.post("/api/v1/auth/otp/request", json={"correo": email})
    assert response.status_code == 202
    return response.json()["desafio_id"], messages[-1][1]


def verify(client, challenge, code):
    return client.post(
        "/api/v1/auth/otp/verify", json={"desafio_id": challenge, "codigo": code}
    )


def test_first_access_session_logout_and_existing_account(identity):
    client, conn, messages, config = identity
    assert client.get("/api/v1/me").status_code == 401
    challenge, code = issue(client, messages)
    stored = (
        conn.execute(select(m.desafio_otp).where(m.desafio_otp.c.id == challenge))
        .mappings()
        .one()
    )
    assert stored["codigo_digest"] != code
    assert stored["codigo_digest"] == auth.digest(challenge + ":" + code)
    result = verify(client, challenge, code)
    assert result.status_code == 200
    uid = result.json()["usuario"]["id"]
    assert result.json()["usuario"]["roles"] == ["estudiante"]
    cookie = result.headers.get_list("set-cookie")[0]
    assert "HttpOnly" in cookie and "SameSite=strict" in cookie
    token = client.cookies.get("previa_session")
    assert (
        conn.scalar(select(m.sesion.c.token_digest).where(m.sesion.c.usuario_id == uid))
        != token
    )
    assert client.get("/api/v1/me").json()["correo"] == EMAIL
    assert verify(client, challenge, code).status_code == 401
    assert client.post("/api/v1/auth/logout", json={}).status_code == 403
    csrf = result.json()["csrf_token"]
    assert (
        client.post("/api/v1/auth/logout", headers={"X-CSRF-Token": csrf}).status_code
        == 204
    )
    assert client.get("/api/v1/me").status_code == 401
    client.cookies.set("previa_session", token, path="/api/v1")
    assert client.get("/api/v1/me").status_code == 401
    client.cookies.clear()
    config.cooldown = 1
    conn.execute(
        update(m.limite_auth)
        .where(
            m.limite_auth.c.clave.in_(
                [
                    auth.digest("emision_correo:" + EMAIL),
                    auth.digest("emision_ip:testclient"),
                ]
            )
        )
        .values(ultimo_en=auth.now() - timedelta(seconds=2))
    )
    second, code2 = issue(client, messages)
    again = verify(client, second, code2)
    assert again.status_code == 200
    assert again.json()["usuario"]["id"] == uid
    assert (
        conn.scalar(
            select(func.count())
            .select_from(m.usuario)
            .where(m.usuario.c.correo_normalizado == EMAIL)
        )
        == 1
    )
    assert (
        conn.scalar(
            select(func.count())
            .select_from(m.perfil_estudiante)
            .where(m.perfil_estudiante.c.usuario_id == uid)
        )
        == 1
    )


def test_incorrect_expired_attempts_and_resend(identity):
    client, conn, messages, config = identity
    challenge, code = issue(client, messages)
    bad = "00000000" if code != "00000000" else "11111111"
    for _ in range(config.attempts):
        assert verify(client, challenge, bad).status_code == 401
    assert verify(client, challenge, code).status_code == 401
    assert (
        conn.scalar(
            select(m.desafio_otp.c.intentos).where(m.desafio_otp.c.id == challenge)
        )
        == config.attempts
    )
    conn.execute(
        update(m.limite_auth)
        .where(
            m.limite_auth.c.clave.in_(
                [
                    auth.digest("emision_correo:" + EMAIL),
                    auth.digest("emision_ip:testclient"),
                ]
            )
        )
        .values(ultimo_en=auth.now() - timedelta(seconds=61))
    )
    second, code2 = issue(client, messages)
    conn.execute(
        update(m.desafio_otp)
        .where(m.desafio_otp.c.id == second)
        .values(expira_en=auth.now() - timedelta(seconds=1))
    )
    assert verify(client, second, code2).status_code == 401
    conn.execute(
        update(m.limite_auth)
        .where(
            m.limite_auth.c.clave.in_(
                [
                    auth.digest("emision_correo:" + EMAIL),
                    auth.digest("emision_ip:testclient"),
                ]
            )
        )
        .values(ultimo_en=auth.now() - timedelta(seconds=61))
    )
    third, code3 = issue(client, messages)
    assert verify(client, challenge, code).status_code == 401
    assert verify(client, third, code3).status_code == 200


def test_resend_invalidates_unused_code(identity):
    client, conn, messages, _ = identity
    first, code = issue(client, messages)
    conn.execute(
        update(m.limite_auth)
        .where(
            m.limite_auth.c.clave.in_(
                [
                    auth.digest("emision_correo:" + EMAIL),
                    auth.digest("emision_ip:testclient"),
                ]
            )
        )
        .values(ultimo_en=auth.now() - timedelta(seconds=61))
    )
    second, code2 = issue(client, messages)
    assert verify(client, first, code).status_code == 401
    assert verify(client, second, code2).status_code == 200


def test_limits_and_generic_domain_response(identity):
    client, _, messages, config = identity
    allowed = client.post("/api/v1/auth/otp/request", json={"correo": EMAIL})
    rejected = client.post(
        "/api/v1/auth/otp/request",
        json={"correo": "test@estudiantes.example.test.evil.invalid"},
    )
    assert allowed.status_code == rejected.status_code == 202
    assert allowed.json()["mensaje"] == rejected.json()["mensaje"]
    assert len(messages) == 1
    assert (
        client.post("/api/v1/auth/otp/request", json={"correo": EMAIL}).status_code
        == 429
    )
    config.ip_limit = 3
    assert (
        client.post(
            "/api/v1/auth/otp/request", json={"correo": "otro@example.invalid"}
        ).status_code
        == 429
    )


def test_suspended_expired_idle_and_csrf_origin(identity):
    client, conn, messages, config = identity
    challenge, code = issue(client, messages)
    result = verify(client, challenge, code)
    uid = result.json()["usuario"]["id"]
    csrf = result.json()["csrf_token"]
    assert (
        client.post(
            "/api/v1/auth/logout",
            headers={"Origin": "http://evil.test", "X-CSRF-Token": csrf},
        ).status_code
        == 403
    )
    conn.execute(update(m.usuario).where(m.usuario.c.id == uid).values(activo=False))
    assert client.get("/api/v1/me").status_code == 401
    conn.execute(update(m.usuario).where(m.usuario.c.id == uid).values(activo=True))
    conn.execute(
        update(m.sesion)
        .where(m.sesion.c.usuario_id == uid)
        .values(ultimo_en=auth.now() - timedelta(seconds=config.idle_seconds))
    )
    assert client.get("/api/v1/me").status_code == 401
    conn.execute(
        update(m.sesion)
        .where(m.sesion.c.usuario_id == uid)
        .values(ultimo_en=auth.now(), expira_en=auth.now())
    )
    assert client.get("/api/v1/me").status_code == 401


def test_shape_origin_normalization_and_roles(identity):
    client, _, messages, _ = identity
    assert (
        client.post(
            "/api/v1/auth/otp/request",
            headers={"Origin": "http://evil.test"},
            json={"correo": EMAIL},
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/api/v1/auth/otp/request", json={"correo": "not-email"}
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/v1/auth/otp/request", json={"correo": EMAIL, "rol": "administrador"}
        ).status_code
        == 422
    )
    assert (
        auth.normalize(" Alice@ESTUDIANTES.EXAMPLE.TEST ")
        == "Alice@estudiantes.example.test"
    )
    challenge, code = issue(client, messages)
    assert (
        client.post(
            "/api/v1/auth/otp/verify",
            json={"desafio_id": challenge, "codigo": code, "roles": ["administrador"]},
        ).status_code
        == 422
    )
    assert verify(client, challenge, "12").status_code == 422
    assert verify(client, challenge, code).json()["usuario"]["roles"] == ["estudiante"]
    cors = client.options(
        "/api/v1/me", headers={**ORIGIN, "Access-Control-Request-Method": "GET"}
    )
    assert cors.headers["access-control-allow-origin"] == ORIGIN["Origin"]
    assert cors.headers["access-control-allow-credentials"] == "true"


def test_mailpit_delivery(identity, monkeypatch):
    client, _, messages, _ = identity
    # SMTP auténtico a Mailpit; no se imprime ni persiste el código fuera del buzón.
    monkeypatch.setattr(auth, "send_code", REAL_SEND)
    email = "smtp-" + secrets.token_hex(8) + "@estudiantes.example.test"
    response = client.post("/api/v1/auth/otp/request", json={"correo": email})
    assert response.status_code == 202
    import json

    with urlopen("http://127.0.0.1:8025/api/v1/messages", timeout=5) as result:
        inbox = json.load(result)
    message = next(
        item
        for item in inbox["messages"]
        if any(to["Address"] == email for to in item["To"])
    )
    with urlopen(
        "http://127.0.0.1:8025/api/v1/message/" + message["ID"], timeout=5
    ) as result:
        detail = json.load(result)
    code = re.search(r"\b[0-9]{8}\b", detail["Text"]).group()
    assert verify(client, response.json()["desafio_id"], code).status_code == 200
    assert messages == []


REAL_SEND = auth.send_code


@pytest.fixture
def concurrent_identity(monkeypatch):
    """Conexiones reales; limpieza limitada a esta ejecución, incluso ante fallos."""
    marker = "h04b-race-" + secrets.token_hex(12)
    email = marker + "@estudiantes.example.test"
    engine = make_engine()
    config = auth.Settings()
    monkeypatch.setattr(auth, "engine", lambda: engine)
    monkeypatch.setattr(auth, "settings", lambda: config)
    messages = []
    monkeypatch.setattr(auth, "send_code", lambda email, code: messages.append(code))

    def tagged_event(conn, kind, user=None):
        conn.execute(
            insert(m.evento_seguridad).values(
                tipo=kind,
                actor_usuario_id=user,
                instante=auth.now(),
                referencia_minima=marker,
            )
        )

    monkeypatch.setattr(auth, "event", tagged_event)
    keys = [
        auth.digest(scope + ":" + value)
        for scope, value in (
            ("emision_correo", email),
            ("emision_ip", marker),
            ("verificacion_ip", marker),
        )
    ]
    try:
        yield engine, email, marker, messages
    finally:
        try:
            with engine.begin() as conn:
                uid = conn.scalar(
                    select(m.usuario.c.id).where(
                        m.usuario.c.correo_normalizado == email
                    )
                )
                conn.execute(
                    delete(m.evento_seguridad).where(
                        m.evento_seguridad.c.referencia_minima == marker
                    )
                )
                if uid is not None:
                    for table in (m.sesion, m.usuario_rol, m.perfil_estudiante):
                        conn.execute(delete(table).where(table.c.usuario_id == uid))
                    conn.execute(delete(m.usuario).where(m.usuario.c.id == uid))
                conn.execute(
                    delete(m.desafio_otp).where(
                        m.desafio_otp.c.correo_normalizado == email
                    )
                )
                conn.execute(
                    delete(m.limite_auth).where(m.limite_auth.c.clave.in_(keys))
                )
            with engine.connect() as conn:
                for table, condition in (
                    (m.usuario, m.usuario.c.correo_normalizado == email),
                    (m.desafio_otp, m.desafio_otp.c.correo_normalizado == email),
                    (
                        m.evento_seguridad,
                        m.evento_seguridad.c.referencia_minima == marker,
                    ),
                    (m.limite_auth, m.limite_auth.c.clave.in_(keys)),
                ):
                    assert (
                        conn.scalar(
                            select(func.count()).select_from(table).where(condition)
                        )
                        == 0
                    )
        finally:
            engine.dispose()


def test_concurrent_consumption_and_requests(concurrent_identity):
    engine, email, ip, messages = concurrent_identity
    barrier = Barrier(2, timeout=10)

    def request_code(_):
        with TestClient(app, headers=ORIGIN, client=(ip, 50000)) as client:
            barrier.wait()
            return client.post("/api/v1/auth/otp/request", json={"correo": email})

    with ThreadPoolExecutor(max_workers=2) as pool:
        issued = list(pool.map(request_code, range(2)))
    assert sorted(r.status_code for r in issued) == [202, 429]
    assert len(messages) == 1
    challenge = next(r for r in issued if r.status_code == 202).json()["desafio_id"]

    def consume(_):
        with TestClient(app, headers=ORIGIN, client=(ip, 50000)) as client:
            barrier.wait()
            return verify(client, challenge, messages[0]).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(consume, range(2))) == [200, 401]
    with engine.connect() as conn:
        uid = conn.scalar(
            select(m.usuario.c.id).where(m.usuario.c.correo_normalizado == email)
        )
        assert uid is not None
        for table in (m.sesion, m.perfil_estudiante, m.usuario_rol):
            assert (
                conn.scalar(
                    select(func.count())
                    .select_from(table)
                    .where(table.c.usuario_id == uid)
                )
                == 1
            )


def test_authentication_failure_rolls_back(identity, monkeypatch):
    client, conn, messages, _ = identity
    challenge, code = issue(client, messages)
    real_event = auth.event

    def fail_session(connection, kind, user=None):
        if kind == "sesion_iniciada":
            raise RuntimeError("Fallo transaccional de prueba")
        return real_event(connection, kind, user)

    monkeypatch.setattr(auth, "event", fail_session)
    with pytest.raises(RuntimeError, match="Fallo transaccional de prueba"):
        verify(client, challenge, code)
    assert (
        conn.scalar(
            select(func.count())
            .select_from(m.usuario)
            .where(m.usuario.c.correo_normalizado == EMAIL)
        )
        == 0
    )
    assert (
        conn.scalar(
            select(m.desafio_otp.c.consumido_en).where(m.desafio_otp.c.id == challenge)
        )
        is None
    )
    monkeypatch.setattr(auth, "event", real_event)
    assert verify(client, challenge, code).status_code == 200


def test_smtp_failure_and_secure_cookie(identity, monkeypatch):
    client, conn, messages, config = identity

    def unavailable(email, code):
        raise OSError("SMTP local no disponible")

    monkeypatch.setattr(auth, "send_code", unavailable)
    response = client.post("/api/v1/auth/otp/request", json={"correo": EMAIL})
    assert response.status_code == 503
    assert (
        conn.scalar(
            select(m.desafio_otp.c.invalidado_en).where(
                m.desafio_otp.c.correo_normalizado == EMAIL
            )
        )
        is not None
    )
    monkeypatch.setattr(
        auth, "send_code", lambda email, code: messages.append((email, code))
    )
    conn.execute(
        update(m.limite_auth)
        .where(
            m.limite_auth.c.clave.in_(
                [
                    auth.digest("emision_correo:" + EMAIL),
                    auth.digest("emision_ip:testclient"),
                ]
            )
        )
        .values(ultimo_en=auth.now() - timedelta(seconds=61))
    )
    challenge, code = issue(client, messages)
    config.secure = True
    response = verify(client, challenge, code)
    assert response.status_code == 200
    assert "Secure" in response.headers.get_list("set-cookie")[0]


def test_suspended_account_cannot_verify(identity):
    client, conn, messages, _ = identity
    challenge, code = issue(client, messages)
    uid = verify(client, challenge, code).json()["usuario"]["id"]
    conn.execute(update(m.usuario).where(m.usuario.c.id == uid).values(activo=False))
    conn.execute(
        update(m.limite_auth)
        .where(
            m.limite_auth.c.clave.in_(
                [
                    auth.digest("emision_correo:" + EMAIL),
                    auth.digest("emision_ip:testclient"),
                ]
            )
        )
        .values(ultimo_en=auth.now() - timedelta(seconds=61))
    )
    challenge, code = issue(client, messages)
    assert verify(client, challenge, code).status_code == 401
    assert client.get("/api/v1/me").status_code == 401
