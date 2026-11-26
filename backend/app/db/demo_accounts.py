"""Provision two safe, fixed local test identities with OTP login via Mailpit.

No passwords or fixed OTP codes are stored. The administrator is not created by
public signup: an explicit command on the local development machine is required.
"""

import argparse

from sqlalchemy import insert, select

from app import auth
from app.db import models as m
from app.db.session import make_engine

STUDENT_EMAIL = "estudiante.demo@estudiantes.example.test"
ADMIN_EMAIL = "admin.demo@estudiantes.example.test"


def provision(conn, email: str, role_name: str) -> int:
    """Idempotent, non-promoting provisioning. Reject any conflicting identity."""
    normalized = auth.normalize(email)
    if normalized != email or email.rsplit("@", 1)[-1] not in auth.settings().domains:
        raise ValueError("Solo se permiten correos de prueba de dominios autorizados.")
    if role_name not in ("estudiante", "administrador"):
        raise ValueError("Rol de prueba no permitido.")

    user = conn.execute(
        select(m.usuario).where(m.usuario.c.correo_normalizado == email).with_for_update()
    ).mappings().first()
    if user is None:
        user_id = conn.execute(insert(m.usuario).values(
            correo_normalizado=email, activo=True,
        )).inserted_primary_key[0]
        new_user = True
    else:
        if not user["activo"]:
            raise ValueError("No se habilitará automáticamente una cuenta desactivada.")
        user_id = user["id"]
        new_user = False

    current_roles = set(conn.execute(
        select(m.rol.c.nombre)
        .join(m.usuario_rol, m.usuario_rol.c.rol_id == m.rol.c.id)
        .where(m.usuario_rol.c.usuario_id == user_id)
    ).scalars().all())
    if current_roles and current_roles != {role_name}:
        raise ValueError(f"La cuenta {email} ya tiene otro rol; no se cambiará automáticamente.")

    profile = conn.scalar(select(m.perfil_estudiante.c.id).where(
        m.perfil_estudiante.c.usuario_id == user_id
    ))
    if role_name == "administrador" and profile:
        raise ValueError("No se permite promocionar una cuenta con perfil estudiantil.")
    if role_name == "estudiante" and not profile:
        conn.execute(insert(m.perfil_estudiante).values(usuario_id=user_id))

    role_id = conn.scalar(select(m.rol.c.id).where(m.rol.c.nombre == role_name))
    if role_id is None:
        role_id = conn.execute(insert(m.rol).values(nombre=role_name)).inserted_primary_key[0]
    if not current_roles:
        conn.execute(insert(m.usuario_rol).values(usuario_id=user_id, rol_id=role_id))
    if new_user:
        conn.execute(insert(m.evento_seguridad).values(
            actor_usuario_id=user_id,
            tipo="cuenta_demo_local_creada",
            instante=auth.now(),
            referencia_minima=role_name,
        ))
    return user_id


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm-local-test", action="store_true", required=True)
    args = parser.parse_args()
    if not args.confirm_local_test:
        parser.error("Esta operación se limita a desarrollo local.")
    engine = make_engine()
    try:
        with engine.begin() as conn:
            auth.lock(conn)
            provision(conn, STUDENT_EMAIL, "estudiante")
            provision(conn, ADMIN_EMAIL, "administrador")
    finally:
        engine.dispose()
    print("Cuentas de prueba listas (acceso por OTP en Mailpit):")
    print("  Estudiante:", STUDENT_EMAIL)
    print("  Administrador:", ADMIN_EMAIL)
    print("No hay contraseñas predeterminadas. El código de 8 dígitos cambia en cada acceso.")


if __name__ == "__main__":
    main()
