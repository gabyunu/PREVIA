"""H05-B: envío y fundamento histórico en MySQL real."""

from datetime import timedelta
from uuid import uuid4

import pytest
import test_auth
from fastapi.testclient import TestClient
from sqlalchemy import func, select, update
from test_auth import pytestmark  # noqa: F401
from test_drafts import body, path, setup

from app import auth
from app.db import models as m
from app.main import app

_identity_fixture = pytest.fixture(name="identity")(test_auth.identity.__wrapped__)


def prepare(identity, empty=False):
    client, conn, pid, ids, rows = setup(identity)
    saved = client.put(path(pid) + "/draft", json=body([] if empty else ids[:1])).json()
    payload = dict(
        revision_esperada=saved["revision_control"],
        revision_perfil=1,
        version_trabajo_id=saved["trabajo"]["id"],
    )
    return client, conn, pid, ids, payload


def send(client, pid, payload, key=None):
    return client.post(
        path(pid) + "/submit",
        json=payload,
        headers={"Idempotency-Key": key or str(uuid4())},
    )


def test_submit_retry_correction_and_immutable_history(identity):
    client, conn, pid, ids, payload = prepare(identity)
    before = conn.execute(select(m.version_solicitud)).mappings().all()
    key = str(uuid4())
    result = send(client, pid, payload, key)
    assert result.status_code == 200, result.text
    sent = result.json()
    assert sent["estado"] == "enviada" and sent["trabajo"] is None
    assert sent["vigente"]["revision_perfil_id"] == before[0]["revision_perfil_id"]
    assert send(client, pid, payload, key).json() == sent
    assert (
        send(client, pid, {**payload, "revision_esperada": 99}, key).status_code == 409
    )
    assert send(client, pid, payload).status_code == 409
    assert conn.scalar(select(func.count()).select_from(m.solicitud)) == 1
    assert conn.scalar(select(func.count()).select_from(m.evento_solicitud)) == 1
    corrected = client.put(
        path(pid) + "/draft", json=body(ids[:1], ["alta"], revision=2)
    ).json()
    assert corrected["vigente"] == sent["vigente"]
    assert corrected["estado"] == "enviada"
    second = send(
        client,
        pid,
        dict(
            revision_esperada=3,
            revision_perfil=1,
            version_trabajo_id=corrected["trabajo"]["id"],
        ),
    )
    assert second.status_code == 200
    assert second.json()["id"] == sent["id"]
    assert (
        conn.execute(
            select(m.version_solicitud).where(
                m.version_solicitud.c.id == before[0]["id"]
            )
        )
        .mappings()
        .one()
        == before[0]
    )
    old_priority = conn.scalar(
        select(m.detalle_solicitud.c.prioridad).where(
            m.detalle_solicitud.c.version_id == sent["vigente"]["id"]
        )
    )
    assert old_priority == "media"


def test_empty_missing_security_and_closed(identity):
    client, conn, pid, ids, payload = prepare(identity, empty=True)
    assert send(client, pid, payload).status_code == 422
    assert send(TestClient(app), pid, payload).status_code == 401
    csrf = client.headers.pop("X-CSRF-Token")
    assert send(client, pid, payload).status_code == 403
    client.headers["X-CSRF-Token"] = csrf
    assert client.post(path(pid) + "/submit", json=payload).status_code == 422
    conn.execute(
        update(m.periodo_academico)
        .where(m.periodo_academico.c.id == pid)
        .values(captura_hasta=auth.now() - timedelta(seconds=1))
    )
    assert send(client, pid, payload).status_code == 409
    assert conn.scalar(select(func.count()).select_from(m.evento_solicitud)) == 0


@pytest.mark.parametrize("state", ["aprobada", None])
def test_changed_profile_blocks_draft_and_invalidates_sent(identity, state):
    client, conn, pid, ids, payload = prepare(identity)
    profile = client.get("/api/v1/me/academic-profile").json()
    states = [s for s in profile["estados"] if s["malla_asignatura_id"] != ids[0]]
    if state:
        states.append(dict(malla_asignatura_id=ids[0], estado=state))
    changed = dict(
        revision_esperada=1,
        malla_id=profile["malla_id"],
        semestre_declarado=1,
        estados=states,
    )
    assert client.put("/api/v1/me/academic-profile", json=changed).status_code == 200
    assert send(client, pid, payload).status_code == 409
    assert send(client, pid, {**payload, "revision_perfil": 2}).status_code == 422


@pytest.mark.parametrize("closed", [False, True])
def test_profile_invalidation_and_closed_history(identity, closed):
    client, conn, pid, ids, payload = prepare(identity)
    key = str(uuid4())
    sent = send(client, pid, payload, key).json()
    if closed:
        conn.execute(
            update(m.periodo_academico)
            .where(m.periodo_academico.c.id == pid)
            .values(captura_hasta=auth.now() - timedelta(seconds=1))
        )
    profile = client.get("/api/v1/me/academic-profile").json()
    result = client.put(
        "/api/v1/me/academic-profile",
        json=dict(
            revision_esperada=1,
            malla_id=profile["malla_id"],
            semestre_declarado=2,
            estados=[],
        ),
    )
    assert result.status_code == 200
    current = client.get(path(pid)).json()
    if closed:
        assert current == sent
    else:
        assert current["estado"] == "invalidada" and current["vigente"] is None
    assert send(client, pid, payload, key).json() == sent


def test_compatible_profile_renews_basis_without_overwriting_work(identity):
    client, conn, pid, ids, payload = prepare(identity)
    sent = send(client, pid, payload).json()
    work = client.put(
        path(pid) + "/draft", json=body(ids[:1], ["alta"], revision=2)
    ).json()["trabajo"]
    profile = client.get("/api/v1/me/academic-profile").json()
    assert (
        client.put(
            "/api/v1/me/academic-profile",
            json=dict(
                revision_esperada=1,
                malla_id=profile["malla_id"],
                semestre_declarado=2,
                estados=profile["estados"],
            ),
        ).status_code
        == 200
    )
    current = client.get(path(pid)).json()
    assert current["trabajo"] == work
    assert current["vigente"]["id"] != sent["vigente"]["id"]
    assert (
        current["vigente"]["revision_perfil_id"]
        != sent["vigente"]["revision_perfil_id"]
    )


def test_submit_revalidates_stored_priorities_and_rules(identity):
    client, conn, pid, ids, payload = prepare(identity)
    # Datos sintéticos alterados por fixture: submit no confía en el guardado previo.
    conn.execute(
        update(m.malla_asignatura)
        .where(m.malla_asignatura.c.id == ids[0])
        .values(revision_pendiente=True)
    )
    assert send(client, pid, payload).status_code == 422
    assert client.get(path(pid)).json()["estado"] == "borrador"


def test_other_student_cannot_submit_foreign_work(identity):
    client, conn, pid, ids, payload = prepare(identity)
    other = TestClient(app, headers=test_auth.ORIGIN)
    login = test_auth.verify(
        other,
        *test_auth.issue(other, identity[2], "h05b-other@estudiantes.example.test"),
    )
    other.headers["X-CSRF-Token"] = login.json()["csrf_token"]
    assert send(other, pid, payload).status_code == 409
    assert client.get(path(pid)).json()["estado"] == "borrador"


_concurrent_fixture = pytest.fixture(name="concurrent_identity")(
    test_auth.concurrent_identity.__wrapped__
)


def test_concurrent_submit_and_retry(concurrent_identity):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    from sqlalchemy import insert

    engine, email, ip, messages = concurrent_identity
    client = TestClient(app, headers=test_auth.ORIGIN, client=(ip, 50000))
    issued = client.post("/api/v1/auth/otp/request", json={"correo": email}).json()
    verified = test_auth.verify(client, issued["desafio_id"], messages[0])
    client.headers["X-CSRF-Token"] = verified.json()["csrf_token"]
    curriculum = client.get("/api/v1/curricula").json()[0]["id"]
    now = auth.now()
    with engine.begin() as conn:
        student = conn.scalar(
            select(m.perfil_estudiante.c.id).where(
                m.perfil_estudiante.c.usuario_id == verified.json()["usuario"]["id"]
            )
        )
        pid = conn.execute(
            insert(m.periodo_academico).values(
                identificador="DEMO-SUBMIT-" + ip,
                inicio_periodo=now + timedelta(days=3),
                captura_desde=now - timedelta(days=1),
                captura_hasta=now + timedelta(days=1),
                zona_horaria="UTC",
                estado_configuracion="publicado",
            )
        ).inserted_primary_key[0]
    try:
        subject = next(
            s
            for s in client.get(f"/api/v1/curricula/{curriculum}").json()["asignaturas"]
            if s["semestre_curricular"] == 1
        )
        # Elegir candidata con reglas verificadas, sin asumir por semestre.
        entries = client.get(f"/api/v1/curricula/{curriculum}").json()["asignaturas"]
        assert (
            client.put(
                "/api/v1/me/academic-profile",
                json=dict(
                    revision_esperada=0,
                    malla_id=curriculum,
                    semestre_declarado=1,
                    estados=[
                        dict(
                            malla_asignatura_id=s["malla_asignatura_id"],
                            estado="no_cursada",
                        )
                        for s in entries
                    ],
                ),
            ).status_code
            == 200
        )
        subject = next(
            s
            for s in client.get("/api/v1/me/eligibility").json()["materias"]
            if s["seleccionable"]
        )
        saved = client.put(
            path(pid) + "/draft", json=body([subject["malla_asignatura_id"]])
        ).json()
        payload = dict(
            revision_esperada=1,
            revision_perfil=1,
            version_trabajo_id=saved["trabajo"]["id"],
        )
        key = str(uuid4())
        barrier = Barrier(2, timeout=10)

        def submit_once(_):
            other = TestClient(app, headers=dict(client.headers), client=(ip, 50000))
            other.cookies.update(client.cookies)
            barrier.wait()
            return send(other, pid, payload, key)

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(submit_once, range(2)))
        assert [r.status_code for r in results] == [200, 200]
        assert results[0].json() == results[1].json()
        assert send(client, pid, payload).status_code == 409
        with engine.connect() as conn:
            sid = saved["id"]
            assert (
                conn.scalar(
                    select(func.count())
                    .select_from(m.evento_solicitud)
                    .where(m.evento_solicitud.c.solicitud_id == sid)
                )
                == 1
            )
            assert (
                conn.scalar(
                    select(func.count())
                    .select_from(m.version_solicitud)
                    .where(m.version_solicitud.c.solicitud_id == sid)
                )
                == 2
            )
    finally:
        with engine.begin() as conn:
            sid = conn.scalar(
                select(m.solicitud.c.id).where(
                    m.solicitud.c.estudiante_id == student,
                    m.solicitud.c.periodo_id == pid,
                )
            )
            if sid:
                conn.execute(
                    m.envio_idempotente.delete().where(
                        m.envio_idempotente.c.estudiante_id == student
                    )
                )
                conn.execute(
                    m.evento_solicitud.delete().where(
                        m.evento_solicitud.c.solicitud_id == sid
                    )
                )
                conn.execute(
                    update(m.solicitud)
                    .where(m.solicitud.c.id == sid)
                    .values(
                        estado="borrador",
                        version_vigente_id=None,
                        version_trabajo_id=None,
                    )
                )
                conn.execute(
                    m.detalle_solicitud.delete().where(
                        m.detalle_solicitud.c.version_id.in_(
                            select(m.version_solicitud.c.id).where(
                                m.version_solicitud.c.solicitud_id == sid
                            )
                        )
                    )
                )
                conn.execute(
                    m.version_solicitud.delete().where(
                        m.version_solicitud.c.solicitud_id == sid
                    )
                )
                conn.execute(m.solicitud.delete().where(m.solicitud.c.id == sid))
            conn.execute(
                m.estado_academico_declarado.delete().where(
                    m.estado_academico_declarado.c.revision_perfil_id.in_(
                        select(m.revision_perfil.c.id).where(
                            m.revision_perfil.c.estudiante_id == student
                        )
                    )
                )
            )
            conn.execute(
                m.revision_perfil.delete().where(
                    m.revision_perfil.c.estudiante_id == student
                )
            )
            conn.execute(
                m.periodo_academico.delete().where(m.periodo_academico.c.id == pid)
            )


@pytest.mark.parametrize(
    "high,low,expected",
    [(3, 4, 200), (0, 4, 200), (4, 0, 422), (0, 5, 422), (1, 6, 422), (2, 5, 422)],
)
def test_submit_priority_limits_independently(identity, high, low, expected):
    from sqlalchemy import insert

    client, conn, pid, ids, payload = prepare(identity, empty=True)
    rows = client.get("/api/v1/me/eligibility").json()["materias"][: high + low]
    entry_ids = [r["malla_asignatura_id"] for r in rows]
    conn.execute(
        update(m.malla_asignatura)
        .where(m.malla_asignatura.c.id.in_(entry_ids))
        .values(
            revision_pendiente=False,
            condiciones_externas=[],
            estado_regla="ninguno_explicito_propuesto",
        )
    )
    conn.execute(
        m.prerrequisito.delete().where(
            m.prerrequisito.c.asignatura_id.in_([r["asignatura_id"] for r in rows])
        )
    )
    # Fixture deliberadamente omite PUT para probar que submit vuelve a contar límites.
    conn.execute(
        insert(m.detalle_solicitud),
        [
            dict(
                version_id=payload["version_trabajo_id"],
                version_malla_id=client.get("/api/v1/me/academic-profile").json()[
                    "malla_id"
                ],
                malla_asignatura_id=sid,
                prioridad="alta" if i < high else "baja",
            )
            for i, sid in enumerate(entry_ids)
        ],
    )
    result = send(client, pid, payload)
    assert result.status_code == expected, result.text


def test_submit_failure_rolls_back_all_effects(identity, monkeypatch):
    from app import drafts

    client, conn, pid, ids, payload = prepare(identity)
    before = client.get(path(pid)).json()
    original = drafts.insert

    def fail(table):
        if table is m.envio_idempotente:
            raise RuntimeError("fallo transaccional simulado")
        return original(table)

    monkeypatch.setattr(drafts, "insert", fail)
    with pytest.raises(RuntimeError, match="fallo transaccional"):
        send(client, pid, payload)
    assert client.get(path(pid)).json() == before
    assert conn.scalar(select(func.count()).select_from(m.version_solicitud)) == 1
    assert conn.scalar(select(func.count()).select_from(m.evento_solicitud)) == 0
    assert conn.scalar(select(func.count()).select_from(m.envio_idempotente)) == 0


def test_browser_preflight_allows_idempotency_header():
    response = TestClient(app).options(
        "/api/v1/me/requests/1/submit",
        headers={
            "Origin": "http://127.0.0.1:4200",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": (
                "content-type,x-csrf-token,idempotency-key"
            ),
        },
    )
    assert response.status_code == 200
    assert "idempotency-key" in response.headers["access-control-allow-headers"].lower()


def test_sent_snapshot_survives_curricular_label_change(identity):
    client, conn, pid, ids, payload = prepare(identity)
    sent = send(client, pid, payload).json()
    vid = sent["vigente"]["id"]
    snapshot = conn.scalar(
        select(m.version_solicitud.c.fundamento).where(m.version_solicitud.c.id == vid)
    )
    assert snapshot["base_datos"] == "AUTODECLARADA"
    candidate = next(
        r for r in snapshot["materias"] if r["malla_asignatura_id"] == ids[0]
    )
    assert candidate["seleccionable"] and candidate["estado_declarado"] == "no_cursada"
    conn.execute(
        update(m.malla_asignatura)
        .where(m.malla_asignatura.c.id == ids[0])
        .values(nombre_publicado="ETIQUETA SINTETICA ALTERADA", revision_pendiente=True)
    )
    assert client.get(path(pid)).json() == sent
    assert (
        conn.scalar(
            select(m.version_solicitud.c.fundamento).where(
                m.version_solicitud.c.id == vid
            )
        )
        == snapshot
    )
