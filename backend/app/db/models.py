"""Tablas H02-A. Las reglas institucionales del piloto siguen provisionales."""

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
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
    Column("fuente_regla", Text),
    Column("regla_revisada_en", DateTime),
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

# Identidad H02-B: tablas aditivas; sin cambios en el catálogo académico.
rol = table("rol", pk(), Column("nombre", String(32), nullable=False, unique=True))
usuario_rol = table(
    "usuario_rol",
    Column("usuario_id", Integer, fk("usuario.id"), primary_key=True),
    Column("rol_id", Integer, fk("rol.id"), primary_key=True),
)
auth_control = table("auth_control", pk())
limite_auth = table(
    "limite_auth",
    Column("clave", String(64), primary_key=True),
    Column("ventana_en", DateTime, nullable=False),
    Column("ultimo_en", DateTime, nullable=False),
    Column("cantidad", Integer, nullable=False),
)
desafio_otp = table(
    "desafio_otp",
    Column("id", String(64), primary_key=True),
    Column("correo_normalizado", String(254), nullable=False, index=True),
    Column("proposito", String(16), nullable=False),
    Column("codigo_digest", String(64), nullable=False),
    Column("emitido_en", DateTime, nullable=False),
    Column("expira_en", DateTime, nullable=False),
    Column("consumido_en", DateTime),
    Column("invalidado_en", DateTime),
    Column("intentos", Integer, nullable=False),
)
sesion = table(
    "sesion",
    pk(),
    Column("usuario_id", Integer, fk("usuario.id"), nullable=False),
    Column("token_digest", String(64), nullable=False, unique=True),
    Column("csrf_digest", String(64), nullable=False),
    Column("creado_en", DateTime, nullable=False),
    Column("ultimo_en", DateTime, nullable=False),
    Column("expira_en", DateTime, nullable=False),
    Column("revocado_en", DateTime),
)
evento_seguridad = table(
    "evento_seguridad",
    pk(),
    Column("actor_usuario_id", Integer, fk("usuario.id")),
    Column("tipo", String(40), nullable=False),
    Column("instante", DateTime, nullable=False),
    Column("referencia_minima", String(64)),
)


# H02-C: planificación orientativa, nunca oferta ni reserva de cupos.
periodo_academico = table(
    "periodo_academico",
    pk(),
    Column("identificador", String(64), nullable=False, unique=True),
    Column("inicio_periodo", DateTime),
    Column("captura_desde", DateTime, nullable=False),
    Column("captura_hasta", DateTime, nullable=False),
    Column("zona_horaria", String(64), nullable=False),
    Column(
        "estado_configuracion", String(16), nullable=False, server_default="borrador"
    ),
    Column("revision_control", Integer, nullable=False, server_default="1"),
    CheckConstraint("captura_desde < captura_hasta", name="orden_captura"),
    CheckConstraint(
        "inicio_periodo IS NULL OR captura_hasta < inicio_periodo",
        name="captura_anterior_destino",
    ),
    CheckConstraint(
        "estado_configuracion IN ('borrador','publicado')", name="estado_valido"
    ),
    CheckConstraint(
        "estado_configuracion = 'borrador' OR inicio_periodo IS NOT NULL",
        name="publicado_con_inicio",
    ),
    CheckConstraint("revision_control > 0", name="revision_positiva"),
)
planificacion_cupos = table(
    "planificacion_cupos",
    pk(),
    Column("malla_asignatura_id", Integer, fk("malla_asignatura.id"), nullable=False),
    Column("periodo_id", Integer, fk("periodo_academico.id"), nullable=False),
    Column("cupos_planificados", Integer),
    Column(
        "actualizado_en",
        DateTime,
        nullable=False,
        server_default=text("(UTC_TIMESTAMP())"),
        onupdate=text("UTC_TIMESTAMP()"),
    ),
    Column("responsable_usuario_id", Integer, fk("usuario.id")),
    UniqueConstraint("malla_asignatura_id", "periodo_id"),
    CheckConstraint("cupos_planificados >= 0", name="cupos_no_negativos"),
    Index("ix_planificacion_cupos_periodo_id", "periodo_id"),
)
nota_administrativa = table(
    "nota_administrativa",
    pk(),
    Column("planificacion_id", Integer, fk("planificacion_cupos.id"), nullable=False),
    Column("autor_usuario_id", Integer, fk("usuario.id"), nullable=False),
    Column("tipo", String(16), nullable=False),
    Column("contenido", Text, nullable=False),
    created(),
    CheckConstraint(
        "tipo IN ('observacion','propuesta','decision')", name="tipo_valido"
    ),
    CheckConstraint("CHAR_LENGTH(TRIM(contenido)) > 0", name="contenido_no_vacio"),
    Index(
        "ix_nota_administrativa_planificacion_fecha",
        "planificacion_id",
        "creado_en",
        "id",
    ),
)

# H05-A: versiones inmutables de trabajo; sin envío ni demanda.
solicitud = table(
    "solicitud",
    Column("id", Integer, primary_key=True, autoincrement="ignore_fk"),
    Column("estudiante_id", Integer, fk("perfil_estudiante.id"), nullable=False),
    Column("periodo_id", Integer, fk("periodo_academico.id"), nullable=False),
    Column("estado", String(16), nullable=False, server_default="borrador"),
    Column("revision_control", Integer, nullable=False, server_default="0"),
    Column("version_trabajo_id", Integer),
    UniqueConstraint("estudiante_id", "periodo_id"),
    UniqueConstraint("id", "estudiante_id"),
    CheckConstraint("estado = 'borrador'", name="estado_h05a"),
    CheckConstraint("revision_control >= 0", name="revision_no_negativa"),
)
version_solicitud = table(
    "version_solicitud",
    pk(),
    Column("solicitud_id", Integer, nullable=False),
    Column("estudiante_id", Integer, nullable=False),
    Column("numero", Integer, nullable=False),
    Column("revision_perfil_id", Integer, nullable=False),
    Column("version_malla_id", Integer, nullable=False),
    created(),
    UniqueConstraint("solicitud_id", "numero"),
    UniqueConstraint("solicitud_id", "id"),
    UniqueConstraint("id", "version_malla_id"),
    ForeignKeyConstraint(
        ["solicitud_id", "estudiante_id"], ["solicitud.id", "solicitud.estudiante_id"]
    ),
    ForeignKeyConstraint(
        ["estudiante_id", "revision_perfil_id"],
        ["revision_perfil.estudiante_id", "revision_perfil.id"],
    ),
    ForeignKeyConstraint(
        ["revision_perfil_id", "version_malla_id"],
        ["revision_perfil.id", "revision_perfil.version_malla_id"],
    ),
    CheckConstraint("numero > 0", name="numero_positivo"),
)
solicitud.append_constraint(
    ForeignKeyConstraint(
        ["id", "version_trabajo_id"],
        ["version_solicitud.solicitud_id", "version_solicitud.id"],
        name="fk_solicitud_trabajo",
        use_alter=True,
    )
)
detalle_solicitud = table(
    "detalle_solicitud",
    Column("version_id", Integer, primary_key=True),
    Column("malla_asignatura_id", Integer, primary_key=True),
    Column("version_malla_id", Integer, nullable=False),
    Column("prioridad", String(8), nullable=False),
    ForeignKeyConstraint(
        ["version_id", "version_malla_id"],
        ["version_solicitud.id", "version_solicitud.version_malla_id"],
    ),
    ForeignKeyConstraint(
        ["malla_asignatura_id", "version_malla_id"],
        ["malla_asignatura.id", "malla_asignatura.version_malla_id"],
    ),
    CheckConstraint("prioridad IN ('alta','media','baja')", name="prioridad_valida"),
)
