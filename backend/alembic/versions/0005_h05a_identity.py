"""Ensure request identity remains generated despite composite pointer FK."""

import sqlalchemy as sa

from alembic import op

revision = "0005_h05a"
down_revision = "0004_h05a"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint(
        "fk_version_solicitud_solicitud_id_solicitud",
        "version_solicitud",
        type_="foreignkey",
    )
    op.drop_constraint("fk_solicitud_trabajo", "solicitud", type_="foreignkey")
    op.alter_column(
        "solicitud",
        "id",
        existing_type=sa.Integer(),
        existing_nullable=False,
        autoincrement=True,
    )
    op.create_foreign_key(
        "fk_version_solicitud_solicitud_id_solicitud",
        "version_solicitud",
        "solicitud",
        ["solicitud_id", "estudiante_id"],
        ["id", "estudiante_id"],
    )
    op.create_foreign_key(
        "fk_solicitud_trabajo",
        "solicitud",
        "version_solicitud",
        ["id", "version_trabajo_id"],
        ["solicitud_id", "id"],
    )


def downgrade():
    pass  # No data or identity destruction on downgrade.
