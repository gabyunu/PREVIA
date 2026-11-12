"""H05-A additive draft storage."""

from alembic import op

revision = "0004_h05a"
down_revision = "6ce839510cac"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""CREATE TABLE solicitud (
	id INTEGER NOT NULL AUTO_INCREMENT,
	estudiante_id INTEGER NOT NULL,
	periodo_id INTEGER NOT NULL,
	estado VARCHAR(16) NOT NULL DEFAULT 'borrador',
	revision_control INTEGER NOT NULL DEFAULT '0',
	version_trabajo_id INTEGER,
	CONSTRAINT pk_solicitud PRIMARY KEY (id),
	CONSTRAINT uq_solicitud_estudiante_id_periodo_id UNIQUE (estudiante_id, periodo_id),
	CONSTRAINT uq_solicitud_id_estudiante_id UNIQUE (id, estudiante_id),
	CONSTRAINT ck_solicitud_estado_h05a CHECK (estado = 'borrador'),
	CONSTRAINT ck_solicitud_revision_no_negativa CHECK (revision_control >= 0),
        CONSTRAINT fk_solicitud_estudiante_id_perfil_estudiante FOREIGN
KEY(estudiante_id) REFERENCES perfil_estudiante (id) ON DELETE RESTRICT ON UPDATE
RESTRICT,
        CONSTRAINT fk_solicitud_periodo_id_periodo_academico FOREIGN KEY(periodo_id)
REFERENCES periodo_academico (id) ON DELETE RESTRICT ON UPDATE RESTRICT
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_as_cs""")
    op.execute("""CREATE TABLE version_solicitud (
	id INTEGER NOT NULL AUTO_INCREMENT,
	solicitud_id INTEGER NOT NULL,
	estudiante_id INTEGER NOT NULL,
	numero INTEGER NOT NULL,
	revision_perfil_id INTEGER NOT NULL,
	version_malla_id INTEGER NOT NULL,
	creado_en DATETIME NOT NULL DEFAULT (UTC_TIMESTAMP()),
	CONSTRAINT pk_version_solicitud PRIMARY KEY (id),
	CONSTRAINT uq_version_solicitud_solicitud_id_numero UNIQUE (solicitud_id, numero),
	CONSTRAINT uq_version_solicitud_solicitud_id_id UNIQUE (solicitud_id, id),
	CONSTRAINT uq_version_solicitud_id_version_malla_id UNIQUE (id, version_malla_id),
        CONSTRAINT fk_version_solicitud_solicitud_id_solicitud FOREIGN
KEY(solicitud_id, estudiante_id) REFERENCES solicitud (id, estudiante_id),
        CONSTRAINT fk_version_solicitud_estudiante_id_revision_perfil FOREIGN
KEY(estudiante_id, revision_perfil_id) REFERENCES revision_perfil (estudiante_id,
id),
        CONSTRAINT fk_version_solicitud_revision_perfil_id_revision_perfil FOREIGN
KEY(revision_perfil_id, version_malla_id) REFERENCES revision_perfil (id,
version_malla_id),
	CONSTRAINT ck_version_solicitud_numero_positivo CHECK (numero > 0)
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_as_cs""")
    op.execute("""CREATE TABLE detalle_solicitud (
	version_id INTEGER NOT NULL,
	malla_asignatura_id INTEGER NOT NULL,
	version_malla_id INTEGER NOT NULL,
	prioridad VARCHAR(8) NOT NULL,
	CONSTRAINT pk_detalle_solicitud PRIMARY KEY (version_id, malla_asignatura_id),
        CONSTRAINT fk_detalle_solicitud_version_id_version_solicitud FOREIGN
KEY(version_id, version_malla_id) REFERENCES version_solicitud (id,
version_malla_id),
        CONSTRAINT fk_detalle_solicitud_malla_asignatura_id_malla_asignatura FOREIGN
KEY(malla_asignatura_id, version_malla_id) REFERENCES malla_asignatura (id,
version_malla_id),
        CONSTRAINT ck_detalle_solicitud_prioridad_valida CHECK (prioridad IN
('alta','media','baja'))
)ENGINE=InnoDB CHARSET=utf8mb4 COLLATE utf8mb4_0900_as_cs""")
    op.create_foreign_key(
        "fk_solicitud_trabajo",
        "solicitud",
        "version_solicitud",
        ["id", "version_trabajo_id"],
        ["solicitud_id", "id"],
    )


def downgrade():
    op.drop_constraint("fk_solicitud_trabajo", "solicitud", type_="foreignkey")
    for name in ("detalle_solicitud", "version_solicitud", "solicitud"):
        op.drop_table(name)
