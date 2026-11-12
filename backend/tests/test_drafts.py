"""H05-A sobre MySQL real, aislado mediante rollback."""

from datetime import timedelta

import pytest
import test_academic
import test_auth
from fastapi.testclient import TestClient
from sqlalchemy import func, insert, select, update
from test_auth import ORIGIN, issue, pytestmark, verify  # noqa: F401

from app import auth, drafts
from app.db import models as m
from app.main import app

_identity_fixture = pytest.fixture(name="identity")(test_auth.identity.__wrapped__)


def setup(identity):
    client, conn, profile, subjects = test_academic.login(identity)
    profile["estados"] = [
        dict(malla_asignatura_id=s["malla_asignatura_id"], estado="no_cursada")
        for s in subjects
    ]
    assert client.put(test_academic.PATH, json=profile).status_code == 200
    now = auth.now()
    pid = conn.execute(
        insert(m.periodo_academico).values(
            identificador="DEMO-TEST-H05A",
            inicio_periodo=now + timedelta(days=3),
            captura_desde=now - timedelta(days=1),
            captura_hasta=now + timedelta(days=1),
            zona_horaria="UTC",
            estado_configuracion="publicado",
        )
    ).inserted_primary_key[0]
    rows = client.get("/api/v1/me/eligibility").json()["materias"]
    enabled = [r["malla_asignatura_id"] for r in rows if r["seleccionable"]]
    return client, conn, pid, enabled, rows


def path(pid):
    return f"/api/v1/me/requests/{pid}"


def body(ids=(), priorities=None, revision=0, profile=1):
    return dict(
        revision_esperada=revision,
        revision_perfil=profile,
        selecciones=[
            dict(malla_asignatura_id=i, prioridad=p)
            for i, p in zip(ids, priorities or ["media"] * len(ids))
        ],
    )


def test_save_modify_history_and_isolation(identity, monkeypatch):
    client, conn, pid, ids, _ = setup(identity)
    assert client.get(path(pid)).status_code == 404
    assert client.get(path(pid) + "?allow_empty=true").json() is None
    first = client.put(path(pid) + "/draft", json=body(ids[:2]))
    assert first.status_code == 200, first.text
    result = first.json()
    assert client.get(path(pid)).json() == result
    assert client.put(path(pid) + "/draft", json=body(ids[:1])).status_code == 409
    second = client.put(path(pid) + "/draft", json=body(ids[:1], ["alta"], 1))
    assert second.status_code == 200
    assert second.json()["id"] == result["id"]
    assert conn.scalar(select(func.count()).select_from(m.solicitud)) == 1
    assert conn.scalar(select(func.count()).select_from(m.version_solicitud)) == 2
    assert (
        len(
            conn.execute(
                select(m.detalle_solicitud).where(
                    m.detalle_solicitud.c.version_id == result["trabajo"]["id"]
                )
            ).all()
        )
        == 2
    )
    other = TestClient(app, headers=ORIGIN)
    login = verify(
        other, *issue(other, identity[2], "h05a-other@estudiantes.example.test")
    )
    other.headers["X-CSRF-Token"] = login.json()["csrf_token"]
    assert other.get(path(pid)).status_code == 404
    assert other.put(path(pid) + "/draft", json=body(ids[:1])).status_code == 409
    assert client.post("/api/v1/auth/logout").status_code == 204
    later = auth.now() + timedelta(seconds=61)
    monkeypatch.setattr(auth, "now", lambda: later)
    verify(client, *issue(client, identity[2]))
    assert client.get(path(pid)).json() == second.json()


def test_security_and_invalid_collection(identity):
    client, conn, pid, ids, rows = setup(identity)
    assert TestClient(app).get(path(pid)).status_code == 401
    assert TestClient(app).put(path(pid) + "/draft", json=body()).status_code == 401
    csrf = client.headers.pop("X-CSRF-Token")
    assert client.put(path(pid) + "/draft", json=body()).status_code == 403
    client.headers["X-CSRF-Token"] = csrf
    assert (
        client.put(
            path(pid) + "/draft", json=body(), headers={"Origin": "http://invalid.test"}
        ).status_code
        == 403
    )
    blocked = next(r["malla_asignatura_id"] for r in rows if not r["seleccionable"])
    for invalid in [
        body([blocked]),
        body([999999]),
        body([ids[0], ids[0]]),
        body(ids[:1], ["urgente"]),
        {**body(), "estudiante_id": 1},
    ]:
        assert client.put(path(pid) + "/draft", json=invalid).status_code == 422
    assert conn.scalar(select(func.count()).select_from(m.solicitud)) == 0
    # D03: aprobada y candidata sin declaración nunca seleccionables.
    profile = client.get(test_academic.PATH).json()
    for states in ([dict(malla_asignatura_id=ids[0], estado="aprobada")], []):
        profile["revision_esperada"] = profile.pop("revision", 1)
        payload = {
            k: profile[k]
            for k in ("revision_esperada", "malla_id", "semestre_declarado")
        }
        assert (
            client.put(
                test_academic.PATH, json={**payload, "estados": states}
            ).status_code
            == 200
        )
        assert (
            client.put(
                path(pid) + "/draft",
                json=body(ids[:1], profile=payload["revision_esperada"] + 1),
            ).status_code
            == 422
        )
        profile = client.get(test_academic.PATH).json()


@pytest.mark.parametrize(
    "high,low,expected",
    [(3, 4, 200), (0, 4, 200), (1, 6, 422), (0, 5, 422), (4, 0, 422), (2, 5, 422)],
)
def test_priority_limits(identity, high, low, expected):
    client, conn, pid, _, rows = setup(identity)
    # Fixture sintético: suficientes candidatas habilitadas para aislar límites.
    ids = [r["malla_asignatura_id"] for r in rows[: high + low]]
    conn.execute(
        update(m.malla_asignatura)
        .where(m.malla_asignatura.c.id.in_(ids))
        .values(
            revision_pendiente=False,
            condiciones_externas=[],
            estado_regla="ninguno_explicito_propuesto",
        )
    )
    conn.execute(
        m.prerrequisito.delete().where(
            m.prerrequisito.c.asignatura_id.in_(
                [r["asignatura_id"] for r in rows[: high + low]]
            )
        )
    )
    result = client.put(
        path(pid) + "/draft", json=body(ids, ["alta"] * high + ["baja"] * low)
    )
    assert result.status_code == expected, result.text


def test_atomic_failure_and_closed_period(identity, monkeypatch):
    client, conn, pid, ids, _ = setup(identity)
    assert client.put(path(pid) + "/draft", json=body(ids[:1])).status_code == 200
    before = client.get(path(pid)).json()
    original = drafts.insert

    def fail(table):
        if table is m.detalle_solicitud:
            raise RuntimeError("fallo simulado")
        return original(table)

    monkeypatch.setattr(drafts, "insert", fail)
    with pytest.raises(RuntimeError, match="fallo simulado"):
        client.put(path(pid) + "/draft", json=body(ids[:2], revision=1))
    assert client.get(path(pid)).json() == before
    assert conn.scalar(select(func.count()).select_from(m.version_solicitud)) == 1
    conn.execute(
        update(m.periodo_academico)
        .where(m.periodo_academico.c.id == pid)
        .values(captura_hasta=auth.now() - timedelta(seconds=1))
    )
    assert client.put(path(pid) + "/draft", json=body(revision=1)).status_code == 409
    assert client.get(path(pid)).json() == before


_concurrent_fixture = pytest.fixture(name="concurrent_identity")(
    test_auth.concurrent_identity.__wrapped__
)


def test_real_concurrent_drafts(concurrent_identity):
    """Dos conexiones reales: una principal y conflicto tanto al crear como editar."""
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    engine, email, ip, messages = concurrent_identity
    client = TestClient(app, headers=ORIGIN, client=(ip, 50000))
    issued = client.post("/api/v1/auth/otp/request", json={"correo": email}).json()
    verified = verify(client, issued["desafio_id"], messages[0])
    client.headers["X-CSRF-Token"] = verified.json()["csrf_token"]
    uid = verified.json()["usuario"]["id"]
    curriculum = client.get("/api/v1/curricula").json()[0]["id"]
    now = auth.now()
    with engine.begin() as conn:
        student = conn.scalar(
            select(m.perfil_estudiante.c.id).where(
                m.perfil_estudiante.c.usuario_id == uid
            )
        )
        pid = conn.execute(
            insert(m.periodo_academico).values(
                identificador="DEMO-RACE-" + ip,
                captura_desde=now - timedelta(days=1),
                captura_hasta=now + timedelta(days=1),
                inicio_periodo=now + timedelta(days=2),
                zona_horaria="UTC",
                estado_configuracion="publicado",
            )
        ).inserted_primary_key[0]
    try:
        assert (
            client.put(
                test_academic.PATH,
                json=dict(
                    revision_esperada=0,
                    malla_id=curriculum,
                    semestre_declarado=1,
                    estados=[],
                ),
            ).status_code
            == 200
        )
        for expected_revision in (0, 1):
            barrier = Barrier(2, timeout=10)

            def save(_):
                other = TestClient(
                    app, headers=dict(client.headers), client=(ip, 50000)
                )
                other.cookies.update(client.cookies)
                barrier.wait()
                return other.put(
                    path(pid) + "/draft", json=body(revision=expected_revision)
                ).status_code

            with ThreadPoolExecutor(max_workers=2) as pool:
                assert sorted(pool.map(save, range(2))) == [200, 409]
        with engine.connect() as conn:
            assert (
                conn.scalar(
                    select(func.count())
                    .select_from(m.solicitud)
                    .where(m.solicitud.c.estudiante_id == student)
                )
                == 1
            )
        assert client.get(path(pid)).json()["revision_control"] == 2
    finally:
        # Solo artefactos sintéticos de esta ejecución, nunca datos previos.
        with engine.begin() as conn:
            sid = conn.scalar(
                select(m.solicitud.c.id).where(
                    m.solicitud.c.estudiante_id == student,
                    m.solicitud.c.periodo_id == pid,
                )
            )
            if sid:
                conn.execute(
                    update(m.solicitud)
                    .where(m.solicitud.c.id == sid)
                    .values(version_trabajo_id=None)
                )
                conn.execute(
                    m.version_solicitud.delete().where(
                        m.version_solicitud.c.solicitud_id == sid
                    )
                )
                conn.execute(m.solicitud.delete().where(m.solicitud.c.id == sid))
            conn.execute(
                m.revision_perfil.delete().where(
                    m.revision_perfil.c.estudiante_id == student
                )
            )
            conn.execute(
                m.periodo_academico.delete().where(m.periodo_academico.c.id == pid)
            )


def test_periods_empty_draft_and_stale_profile(identity):
    client, conn, pid, ids, _ = setup(identity)
    periods = client.get("/api/v1/periods").json()
    assert next(p for p in periods if p["id"] == pid)["captura_abierta"]
    assert (
        client.put(path(pid) + "/draft", json=body(ids[:1], profile=2)).status_code
        == 409
    )
    assert client.put(path(pid) + "/draft", json=body()).status_code == 200
    assert client.get(path(pid)).json()["trabajo"]["selecciones"] == []
    assert (
        client.put(
            path(pid) + "/draft",
            json=body(list(range(1, 9)), ["alta"] * 3 + ["media"] * 5, revision=1),
        ).status_code
        == 422
    )
    conn.execute(
        update(m.periodo_academico)
        .where(m.periodo_academico.c.id == pid)
        .values(estado_configuracion="borrador")
    )
    assert pid not in [p["id"] for p in client.get("/api/v1/periods").json()]
    assert client.get(path(pid)).status_code == 404


def test_existing_subject_from_other_curriculum(identity):
    client, conn, pid, _, _ = setup(identity)
    entry = conn.execute(select(m.malla_asignatura)).mappings().first()
    career = conn.scalar(
        select(m.version_malla.c.carrera_id).where(
            m.version_malla.c.id == entry["version_malla_id"]
        )
    )
    other = conn.execute(
        insert(m.version_malla).values(
            carrera_id=career, codigo_version="DEMO-H05A-AJENA"
        )
    ).inserted_primary_key[0]
    other_id = conn.execute(
        insert(m.malla_asignatura).values(
            **{k: v for k, v in entry.items() if k != "id"}
            | {"version_malla_id": other}
        )
    ).inserted_primary_key[0]
    result = client.put(path(pid) + "/draft", json=body([other_id]))
    assert result.status_code == 422
    assert result.json()["error"]["codigo"] == "fuera_de_malla"
    assert client.get(path(pid)).status_code == 404
