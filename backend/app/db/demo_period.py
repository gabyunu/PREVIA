"""Período sintético explícito, idempotente; no altera períodos ni cupos existentes."""

from datetime import timedelta

from sqlalchemy import insert, select

from app import auth
from app.db import models as m
from app.db.session import make_engine


def main():
    engine = make_engine()
    with engine.begin() as conn:
        auth.lock(conn)
        now = auth.now()
        code = "DEMOSTRACION-H05A-" + now.strftime("%Y%m%d")
        existing = conn.scalar(
            select(m.periodo_academico.c.id).where(
                m.periodo_academico.c.identificador == code
            )
        )
        if not existing:
            conn.execute(
                insert(m.periodo_academico).values(
                    identificador=code,
                    captura_desde=now - timedelta(minutes=1),
                    captura_hasta=now + timedelta(days=7),
                    inicio_periodo=now + timedelta(days=8),
                    zona_horaria="America/Guayaquil",
                    estado_configuracion="publicado",
                )
            )
        print(code + " · datos sintéticos DEMOSTRACIÓN; sin fechas institucionales")
    engine.dispose()


if __name__ == "__main__":
    main()
