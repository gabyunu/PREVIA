"""Concesión local explícita a cuenta existente sin historial académico."""

import argparse

from sqlalchemy import delete, insert, select

from app import auth
from app.db import models as m
from app.db.session import make_engine


def grant(conn, user_id, operator):
    auth.lock(conn)
    user = (
        conn.execute(
            select(m.usuario).where(m.usuario.c.id == user_id).with_for_update()
        )
        .mappings()
        .first()
    )
    if not user or not user["activo"]:
        raise ValueError("Se requiere una cuenta OTP existente y activa.")
    profile = conn.scalar(
        select(m.perfil_estudiante.c.id).where(
            m.perfil_estudiante.c.usuario_id == user_id
        )
    )
    if profile and conn.scalar(
        select(m.revision_perfil.c.id)
        .where(m.revision_perfil.c.estudiante_id == profile)
        .limit(1)
    ):
        raise ValueError("Usa una cuenta de pruebas separada, sin historial académico.")
    admin = conn.scalar(select(m.rol.c.id).where(m.rol.c.nombre == "administrador"))
    if not admin:
        admin = conn.execute(
            insert(m.rol).values(nombre="administrador")
        ).inserted_primary_key[0]
    existing = conn.scalar(
        select(m.usuario_rol.c.usuario_id).where(
            m.usuario_rol.c.usuario_id == user_id, m.usuario_rol.c.rol_id == admin
        )
    )
    if not existing:
        conn.execute(insert(m.usuario_rol).values(usuario_id=user_id, rol_id=admin))
    student = select(m.rol.c.id).where(m.rol.c.nombre == "estudiante")
    conn.execute(
        delete(m.usuario_rol).where(
            m.usuario_rol.c.usuario_id == user_id, m.usuario_rol.c.rol_id.in_(student)
        )
    )
    conn.execute(
        insert(m.evento_seguridad).values(
            actor_usuario_id=user_id,
            tipo="admin_local_concedido",
            instante=auth.now(),
            referencia_minima=operator,
        )
    )
    conn.execute(
        m.sesion.update()
        .where(m.sesion.c.usuario_id == user_id)
        .values(revocado_en=auth.now())
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user-id", type=int, required=True)
    parser.add_argument(
        "--operator",
        required=True,
        help="Referencia local del operador, sin secretos (1–64 caracteres)",
    )
    parser.add_argument("--confirm-local-test", action="store_true", required=True)
    args = parser.parse_args()
    if not 1 <= len(args.operator.strip()) <= 64:
        parser.error("Referencia de operador inválida.")
    engine = make_engine()
    try:
        with engine.begin() as conn:
            grant(conn, args.user_id, args.operator.strip())
    finally:
        engine.dispose()
    print(
        "Acceso administrativo local configurado y auditado. "
        "Inicia sesión con OTP nuevo."
    )


if __name__ == "__main__":
    main()
