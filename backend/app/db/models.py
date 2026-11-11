"""Tablas H02-A. Las reglas institucionales del piloto siguen provisionales."""

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(table_name)s_%(column_0_name)s",
            "uq": "uq_%(table_name)s_%(column_0_N_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


def fk(target):
    return ForeignKey(target, ondelete="RESTRICT", onupdate="RESTRICT")


def table(name, *columns):
    return Table(
        name,
        Base.metadata,
        *columns,
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_0900_as_cs",
    )


def pk():
    return Column("id", Integer, primary_key=True)


def created():
    # MySQL guarda DATETIME sin zona: toda escritura usa UTC.
    return Column(
        "creado_en", DateTime, nullable=False, server_default=text("(UTC_TIMESTAMP())")
    )


carrera = table(
    "carrera",
    pk(),
    Column("codigo", String(64), nullable=False, unique=True),
    Column("nombre", String(255), nullable=False),
)
version_malla = table(
    "version_malla",
    pk(),
    Column("carrera_id", Integer, fk("carrera.id"), nullable=False),
    Column("codigo_version", String(64), nullable=False),
    Column("estado_publicacion", String(16), nullable=False, server_default="borrador"),
    Column("revision_control", Integer, nullable=False, server_default="1"),
    UniqueConstraint("carrera_id", "codigo_version"),
    CheckConstraint(
        "estado_publicacion IN ('borrador','publicada')", name="publicacion"
    ),
    CheckConstraint("revision_control > 0", name="revision_positiva"),
)
asignatura = table(
    "asignatura",
    pk(),
    Column("identificador_catalogo", String(96), nullable=False, unique=True),
    Column("nombre", String(255), nullable=False),
)
malla_asignatura = table(
    "malla_asignatura",
    pk(),
    Column("version_malla_id", Integer, fk("version_malla.id"), nullable=False),
    Column("asignatura_id", Integer, fk("asignatura.id"), nullable=False),
    Column("semestre_curricular", Integer, nullable=False),
    Column("codigo_publicado", String(64)),
    Column("nombre_publicado", String(255), nullable=False),
    Column("estado_regla", String(64), nullable=False),
    Column("revision_pendiente", Boolean, nullable=False),
    Column("prerrequisito_texto_original", Text, nullable=False),
    # Solo condiciones externas textuales; las aristas internas son relacionales.
    Column("condiciones_externas", JSON, nullable=False),
    UniqueConstraint("version_malla_id", "asignatura_id"),
    UniqueConstraint("id", "version_malla_id"),
    CheckConstraint("semestre_curricular > 0", name="semestre_positivo"),
    CheckConstraint(
        "estado_regla IN ('ninguno_explicito_propuesto',"
        "'prerrequisitos_asignaturas_propuestos','ninguno_identificado_sin_confirmar',"
        "'prerrequisito_fuera_de_malla','depende_del_itinerario_no_definido',"
        "'requisito_no_definido')",
        name="regla_conocida",
    ),
)
prerrequisito = table(
    "prerrequisito",
    Column("version_malla_id", Integer, primary_key=True),
    Column("asignatura_id", Integer, primary_key=True),
    Column("requisito_asignatura_id", Integer, primary_key=True),
    ForeignKeyConstraint(
        ["version_malla_id", "asignatura_id"],
        ["malla_asignatura.version_malla_id", "malla_asignatura.asignatura_id"],
        ondelete="RESTRICT",
        onupdate="RESTRICT",
    ),
    ForeignKeyConstraint(
        ["version_malla_id", "requisito_asignatura_id"],
        ["malla_asignatura.version_malla_id", "malla_asignatura.asignatura_id"],
        name="fk_prerrequisito_requisito",
        ondelete="RESTRICT",
        onupdate="RESTRICT",
    ),
    CheckConstraint(
        "asignatura_id <> requisito_asignatura_id", name="no_autorreferencia"
    ),
)
usuario = table(
    "usuario",
    pk(),
    Column("correo_normalizado", String(254), nullable=False, unique=True),
    created(),
    Column("activo", Boolean, nullable=False, server_default=text("1")),
)
perfil_estudiante = table(
    "perfil_estudiante",
    pk(),
    Column("usuario_id", Integer, fk("usuario.id"), nullable=False, unique=True),
)
revision_perfil = table(
    "revision_perfil",
    pk(),
    Column("estudiante_id", Integer, fk("perfil_estudiante.id"), nullable=False),
    Column("numero", Integer, nullable=False),
    Column("version_malla_id", Integer, fk("version_malla.id"), nullable=False),
    Column("semestre_declarado", Integer, nullable=False),
    created(),
    UniqueConstraint("estudiante_id", "numero"),
    UniqueConstraint("estudiante_id", "id"),
    UniqueConstraint("id", "version_malla_id"),
    CheckConstraint("numero > 0", name="numero_positivo"),
    CheckConstraint("semestre_declarado > 0", name="semestre_positivo"),
)
estado_academico_declarado = table(
    "estado_academico_declarado",
    Column("revision_perfil_id", Integer, primary_key=True),
    Column("malla_asignatura_id", Integer, primary_key=True),
    Column("version_malla_id", Integer, nullable=False),
    Column("estado", String(16), nullable=False),
    ForeignKeyConstraint(
        ["revision_perfil_id", "version_malla_id"],
        ["revision_perfil.id", "revision_perfil.version_malla_id"],
        ondelete="RESTRICT",
        onupdate="RESTRICT",
    ),
    ForeignKeyConstraint(
        ["malla_asignatura_id", "version_malla_id"],
        ["malla_asignatura.id", "malla_asignatura.version_malla_id"],
        name="fk_estado_entrada_malla",
        ondelete="RESTRICT",
        onupdate="RESTRICT",
    ),
    CheckConstraint(
        "estado IN ('aprobada','reprobada','no_cursada')", name="estado_valido"
    ),
)
