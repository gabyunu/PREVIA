"""Role-account provisioning tests without MySQL or Flask dependencies."""

import os

import pytest
from sqlalchemy import create_engine, event, select

from app.db import models as m
from app.db.demo_accounts import ADMIN_EMAIL, STUDENT_EMAIL, provision


def test_local_accounts_are_exclusive_idempotent_and_never_promoted(monkeypatch):
    monkeypatch.setenv("AUTH_HMAC_KEY", "0123456789abcdef" * 4)
    monkeypatch.setenv("AUTH_ALLOWED_DOMAINS", "estudiantes.example.test")
    from app import auth
    auth.settings.cache_clear()
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def sqlite_functions(connection, _):
        connection.create_function("UTC_TIMESTAMP", 0, lambda: "2026-11-23 00:00:00")
        connection.execute("PRAGMA foreign_keys=ON")

    with engine.begin() as conn:
        for table in (m.usuario, m.rol, m.perfil_estudiante, m.usuario_rol, m.evento_seguridad):
            table.create(conn)
        student_id = provision(conn, STUDENT_EMAIL, "estudiante")
        admin_id = provision(conn, ADMIN_EMAIL, "administrador")
        assert student_id != admin_id
        assert provision(conn, STUDENT_EMAIL, "estudiante") == student_id
        assert provision(conn, ADMIN_EMAIL, "administrador") == admin_id
        assert conn.scalar(select(m.perfil_estudiante.c.id).where(m.perfil_estudiante.c.usuario_id == student_id)) is not None
        assert conn.scalar(select(m.perfil_estudiante.c.id).where(m.perfil_estudiante.c.usuario_id == admin_id)) is None
        assert len(conn.execute(select(m.usuario)).all()) == 2
        assert len(conn.execute(select(m.usuario_rol)).all()) == 2
        with pytest.raises(ValueError, match="otro rol"):
            provision(conn, STUDENT_EMAIL, "administrador")
        with pytest.raises(ValueError, match="otro rol"):
            provision(conn, ADMIN_EMAIL, "estudiante")
        with pytest.raises(ValueError):
            provision(conn, "admin@other.example.test", "administrador")
    engine.dispose()
    auth.settings.cache_clear()
