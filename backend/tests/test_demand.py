"""H06 sobre MySQL: mismas versiones y transiciones reales de H05."""

import csv
import io

import pytest
import test_auth
from fastapi.testclient import TestClient
from sqlalchemy import insert, select, update
from test_auth import pytestmark  # noqa: F401
from test_drafts import body, path
from test_submit import prepare, send

from app.db import models as m
from app.db.admin_access import grant
from app.main import app

_identity_fixture = pytest.fixture(name="identity")(test_auth.identity.__wrapped__)
BASE = "/api/v1/admin/demand"


def admin(identity):
    client, conn, messages, _ = identity
    other = TestClient(app, headers=test_auth.ORIGIN)
    result = test_auth.verify(
        other, *test_auth.issue(other, messages, "h06-admin@estudiantes.example.test")
    )
    uid = result.json()["usuario"]["id"]
    role = conn.scalar(select(m.rol.c.id).where(m.rol.c.nombre == "administrador"))
    if not role:
        role = conn.execute(
            insert(m.rol).values(nombre="administrador")
        ).inserted_primary_key[0]
    conn.execute(insert(m.usuario_rol).values(usuario_id=uid, rol_id=role))
    return other


def report(client, pid, **filters):
    response = client.get(BASE, params=dict(periodo_id=pid, **filters))
    assert response.status_code == 200, response.text
    return response.json()


def test_drafts_corrections_priorities_capacity_csv(identity):
    student, conn, pid, ids, payload = prepare(identity)
    reader = admin(identity)
    assert report(reader, pid)["intenciones"] == 0
    sent = send(student, pid, payload).json()
    first = report(reader, pid)
    assert (first["estudiantes"], first["intenciones"], first["media"]) == (1, 1, 1)
    assert first["filas"][0]["cupos_planificados"] is None
    conn.execute(
        insert(m.planificacion_cupos).values(
            periodo_id=pid, malla_asignatura_id=ids[0], cupos_planificados=None
        )
    )
    assert report(reader, pid)["filas"][0]["cupos_planificados"] is None
    conn.execute(
        update(m.planificacion_cupos)
        .where(m.planificacion_cupos.c.periodo_id == pid)
        .values(cupos_planificados=0)
    )
    saved = student.put(
        path(pid) + "/draft", json=body(ids[:3], ["alta", "media", "baja"], revision=2)
    ).json()
    assert report(reader, pid)["intenciones"] == 1
    assert (
        send(
            student,
            pid,
            dict(
                revision_esperada=3,
                revision_perfil=1,
                version_trabajo_id=saved["trabajo"]["id"],
            ),
        ).status_code
        == 200
    )
    data = report(reader, pid, tamano_grupo=2)
    assert (data["estudiantes"], data["intenciones"], data["asignaturas"]) == (1, 3, 3)
    assert (data["alta"], data["media"], data["baja"]) == (1, 1, 1)
    assert all(r["grupos"] == 1 for r in data["filas"])
    assert (
        next(r for r in data["filas"] if r["asignatura_id"] == ids[0])[
            "cupos_planificados"
        ]
        == 0
    )
    filtered = report(reader, pid, prioridad="alta")
    assert filtered["intenciones"] == filtered["estudiantes"] == 1
    assert report(reader, pid, q="NO-EXISTE")["estudiantes"] == 0
    assert report(reader, pid, malla_id=999999)["filas"] == []
    csv_response = reader.get(
        BASE, params=dict(periodo_id=pid, prioridad="alta", formato="csv")
    )
    assert csv_response.status_code == 200
    rows = list(csv.reader(io.StringIO(csv_response.text.lstrip("\ufeff"))))
    assert rows[4][0] == "periodo_id" and len(rows) == 6
    assert rows[5][8:12] == ["1", "1", "0", "0"]
    assert "@estudiantes" not in csv_response.text
    assert csv_response.headers["cache-control"] == "no-store"
    assert sent["vigente"]["id"] != student.get(path(pid)).json()["vigente"]["id"]


@pytest.mark.parametrize("closed", [False, True])
def test_invalidation_and_closed_snapshot(identity, closed):
    from datetime import timedelta

    from app import auth

    student, conn, pid, ids, payload = prepare(identity)
    reader = admin(identity)
    assert send(student, pid, payload).status_code == 200
    if closed:
        conn.execute(
            update(m.periodo_academico)
            .where(m.periodo_academico.c.id == pid)
            .values(captura_hasta=auth.now() - timedelta(seconds=1))
        )
    profile = student.get("/api/v1/me/academic-profile").json()
    assert (
        student.put(
            "/api/v1/me/academic-profile",
            json=dict(
                revision_esperada=1,
                malla_id=profile["malla_id"],
                semestre_declarado=2,
                estados=[],
            ),
        ).status_code
        == 200
    )
    assert report(reader, pid)["intenciones"] == int(closed)


def test_permissions_and_controlled_admin(identity):
    student, conn, pid, ids, payload = prepare(identity)
    assert TestClient(app).get(BASE).status_code == 401
    assert TestClient(app).get(BASE + "?formato=csv").status_code == 401
    assert student.get(BASE).status_code == 403
    assert student.get(BASE + "/options").status_code == 403
    assert student.get(BASE + "?formato=csv").status_code == 403
    uid = student.get("/api/v1/me").json()["id"]
    with pytest.raises(ValueError, match="sin historial"):
        grant(conn, uid, "test-h06")
    reader = admin(identity)
    admin_uid = reader.get("/api/v1/me").json()["id"]
    grant(conn, admin_uid, "test-h06")
    assert reader.get(BASE).status_code == 401  # Revoca sesiones previas.
    assert conn.scalar(
        select(m.evento_seguridad.c.id).where(
            m.evento_seguridad.c.tipo == "admin_local_concedido"
        )
    )
    assert "administrador" not in student.get("/api/v1/me").json()["roles"]


def test_period_curriculum_separation_and_snapshot(identity):
    student, conn, pid, ids, payload = prepare(identity)
    reader = admin(identity)
    sent = send(student, pid, payload).json()
    original = report(reader, pid)["filas"][0]
    conn.execute(
        update(m.malla_asignatura)
        .where(m.malla_asignatura.c.id == ids[0])
        .values(nombre_publicado="=FORMULA")
    )
    assert report(reader, pid)["filas"][0]["nombre"] == original["nombre"]
    # Segunda solicitud del mismo estudiante en otro período: DISTINCT global.
    period = dict(
        conn.execute(select(m.periodo_academico).where(m.periodo_academico.c.id == pid))
        .mappings()
        .one()
    )
    period.pop("id")
    period["identificador"] += "-OTRO"
    second_pid = conn.execute(
        insert(m.periodo_academico).values(**period)
    ).inserted_primary_key[0]
    saved = student.put(path(second_pid) + "/draft", json=body(ids[:1])).json()
    assert (
        send(
            student,
            second_pid,
            dict(
                revision_esperada=1,
                revision_perfil=1,
                version_trabajo_id=saved["trabajo"]["id"],
            ),
        ).status_code
        == 200
    )
    assert report(reader, second_pid)["intenciones"] == 1
    all_data = reader.get(BASE).json()
    relevant = [r for r in all_data["filas"] if r["periodo_id"] in (pid, second_pid)]
    assert len(relevant) == 2
    # Una versión curricular distinta queda fuera del filtro anterior.
    version = (
        conn.execute(
            select(m.version_malla).where(m.version_malla.c.id == original["malla_id"])
        )
        .mappings()
        .one()
    )
    new_id = conn.execute(
        insert(m.version_malla).values(
            carrera_id=version["carrera_id"], codigo_version="DEMO-H06-SEPARADA"
        )
    ).inserted_primary_key[0]
    assert report(reader, pid, malla_id=new_id)["intenciones"] == 0
    assert report(reader, pid, malla_id=sent["vigente"]["malla_id"])["intenciones"] == 1


def test_csv_formula_guard():
    from app.demand import safe_cell

    for text in ("=1+1", " +1", "\t@x", "-1"):
        assert safe_cell(text).startswith("'")
    assert safe_cell(0) == 0


def test_two_students_shared_subject_separate_curricula(identity):
    student, conn, pid, ids, payload = prepare(identity)
    reader = admin(identity)
    sent = send(student, pid, payload).json()
    original = report(reader, pid)["filas"][0]
    curriculum = (
        conn.execute(
            select(m.version_malla).where(m.version_malla.c.id == original["malla_id"])
        )
        .mappings()
        .one()
    )
    mid = conn.execute(
        insert(m.version_malla).values(
            carrera_id=curriculum["carrera_id"], codigo_version="DEMO-H06-OTRA"
        )
    ).inserted_primary_key[0]
    entry = dict(
        conn.execute(
            select(m.malla_asignatura).where(m.malla_asignatura.c.id == ids[0])
        )
        .mappings()
        .one()
    )
    entry.pop("id")
    entry["version_malla_id"] = mid
    eid = conn.execute(insert(m.malla_asignatura).values(**entry)).inserted_primary_key[
        0
    ]
    uid = conn.execute(
        insert(m.usuario).values(
            correo_normalizado="h06-second@estudiantes.example.test"
        )
    ).inserted_primary_key[0]
    sid = conn.execute(
        insert(m.perfil_estudiante).values(usuario_id=uid)
    ).inserted_primary_key[0]
    rid = conn.execute(
        insert(m.revision_perfil).values(
            estudiante_id=sid, numero=1, version_malla_id=mid, semestre_declarado=1
        )
    ).inserted_primary_key[0]
    main = conn.execute(
        insert(m.solicitud).values(estudiante_id=sid, periodo_id=pid)
    ).inserted_primary_key[0]
    vid = conn.execute(
        insert(m.version_solicitud).values(
            solicitud_id=main,
            estudiante_id=sid,
            numero=1,
            revision_perfil_id=rid,
            version_malla_id=mid,
            fundamento={
                "materias": [
                    {
                        "malla_asignatura_id": eid,
                        "nombre": original["nombre"],
                        "semestre_curricular": 2,
                        "estado_declarado": "reprobada",
                    }
                ]
            },
        )
    ).inserted_primary_key[0]
    conn.execute(
        insert(m.detalle_solicitud).values(
            version_id=vid,
            malla_asignatura_id=eid,
            version_malla_id=mid,
            prioridad="baja",
        )
    )
    conn.execute(
        update(m.solicitud)
        .where(m.solicitud.c.id == main)
        .values(estado="enviada", version_vigente_id=vid)
    )
    data = report(reader, pid)
    assert (data["estudiantes"], data["intenciones"], data["asignaturas"]) == (2, 2, 2)
    assert len(data["filas"]) == 2
    assert report(reader, pid, malla_id=mid)["filas"][0]["repeticion"] == 1
    assert report(reader, pid, malla_id=sent["vigente"]["malla_id"])["media"] == 1
    assert report(reader, pid, semestre=2)["baja"] == 1
    assert report(reader, pid, orden="ascending")["intenciones"] == 2
    assert report(reader, pid, orden="name")["intenciones"] == 2
    assert (
        report(reader, pid, orden="semester")["filas"][0]["semestre"]
        == original["semestre"]
    )
    # Una cuenta administrativa suspendida pierde acceso al reporte.
    admin_id = reader.get("/api/v1/me").json()["id"]
    conn.execute(
        update(m.usuario).where(m.usuario.c.id == admin_id).values(activo=False)
    )
    assert reader.get(BASE).status_code == 401
