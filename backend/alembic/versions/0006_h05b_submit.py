"""H05-B: vigencia, auditoría e idempotencia, sin alterar datos existentes."""

import sqlalchemy as sa

from alembic import op

revision = "0006_h05b"
down_revision = "0005_h05a"
branch_labels = None
depends_on = None


def upgrade():
    if "version_vigente_id" not in {
        c["name"] for c in sa.inspect(op.get_bind()).get_columns("solicitud")
    }:
        op.add_column("solicitud", sa.Column("version_vigente_id", sa.Integer()))
    op.drop_constraint(op.f("ck_solicitud_estado_h05a"), "solicitud", type_="check")
    op.create_check_constraint(
        "estado_h05b", "solicitud", "estado IN ('borrador','enviada','invalidada')"
    )
    op.create_check_constraint(
        "vigencia_h05b",
        "solicitud",
        "(estado = 'enviada' AND version_vigente_id IS NOT NULL) OR "
        "(estado != 'enviada' AND version_vigente_id IS NULL)",
    )
    op.create_foreign_key(
        "fk_solicitud_vigente",
        "solicitud",
        "version_solicitud",
        ["id", "version_vigente_id"],
        ["solicitud_id", "id"],
    )
    op.create_table(
        "evento_solicitud",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("solicitud_id", sa.Integer(), nullable=False),
        sa.Column("version_id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(24), nullable=False),
        sa.Column(
            "creado_en",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["solicitud_id", "version_id"],
            ["version_solicitud.solicitud_id", "version_solicitud.id"],
        ),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_table(
        "envio_idempotente",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "estudiante_id",
            sa.Integer(),
            sa.ForeignKey(
                "perfil_estudiante.id", ondelete="RESTRICT", onupdate="RESTRICT"
            ),
            nullable=False,
        ),
        sa.Column(
            "periodo_id",
            sa.Integer(),
            sa.ForeignKey(
                "periodo_academico.id", ondelete="RESTRICT", onupdate="RESTRICT"
            ),
            nullable=False,
        ),
        sa.Column("clave", sa.String(36), nullable=False),
        sa.Column("huella", sa.String(64), nullable=False),
        sa.Column("respuesta", sa.JSON(), nullable=False),
        sa.Column(
            "creado_en",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint("estudiante_id", "periodo_id", "clave"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )


def downgrade():
    raise RuntimeError("H05-B conserva históricos: downgrade destructivo no soportado.")
