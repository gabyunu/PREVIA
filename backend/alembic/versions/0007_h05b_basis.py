"""Conservar evaluación utilizada sin reinterpretar reglas históricas."""

import sqlalchemy as sa

from alembic import op

revision = "0007_h05b"
down_revision = "0006_h05b"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("version_solicitud", sa.Column("fundamento", sa.JSON()))


def downgrade():
    raise RuntimeError("El fundamento histórico no se elimina automáticamente.")
