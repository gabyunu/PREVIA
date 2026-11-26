-- PREVIA MySQL 8.4: database schema derived from SQLAlchemy metadata.

-- FOR AN EMPTY DEMO DATABASE ONLY. Prefer Alembic migrations for normal setup.

-- No DROP / destructive statements are included.

CREATE DATABASE IF NOT EXISTS `previa_dev` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_cs;

USE `previa_dev`;




CREATE TABLE carrera (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	codigo VARCHAR(64) NOT NULL, 
	nombre VARCHAR(255) NOT NULL, 
	CONSTRAINT pk_carrera PRIMARY KEY (id), 
	CONSTRAINT uq_carrera_codigo UNIQUE (codigo)
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_0900_as_cs;


CREATE TABLE version_malla (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	carrera_id INTEGER NOT NULL, 
	codigo_version VARCHAR(64) NOT NULL, 
	estado_publicacion VARCHAR(16) NOT NULL DEFAULT 'borrador', 
	revision_control INTEGER NOT NULL DEFAULT '1', 
	CONSTRAINT pk_version_malla PRIMARY KEY (id), 
	CONSTRAINT uq_version_malla_carrera_id_codigo_version UNIQUE (carrera_id, codigo_version), 
	CONSTRAINT ck_version_malla_publicacion CHECK (estado_publicacion IN ('borrador','publicada')), 
	CONSTRAINT ck_version_malla_revision_positiva CHECK (revision_control > 0)
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_0900_as_cs;


CREATE TABLE asignatura (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	identificador_catalogo VARCHAR(96) NOT NULL, 
	nombre VARCHAR(255) NOT NULL, 
	CONSTRAINT pk_asignatura PRIMARY KEY (id), 
	CONSTRAINT uq_asignatura_identificador_catalogo UNIQUE (identificador_catalogo)
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_0900_as_cs;


CREATE TABLE malla_asignatura (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	version_malla_id INTEGER NOT NULL, 
	asignatura_id INTEGER NOT NULL, 
	semestre_curricular INTEGER NOT NULL, 
	codigo_publicado VARCHAR(64), 
	nombre_publicado VARCHAR(255) NOT NULL, 
	estado_regla VARCHAR(64) NOT NULL, 
	revision_pendiente BOOL NOT NULL, 
	prerrequisito_texto_original TEXT NOT NULL, 
	condiciones_externas JSON NOT NULL, 
	fuente_regla TEXT, 
	regla_revisada_en DATETIME, 
	CONSTRAINT pk_malla_asignatura PRIMARY KEY (id), 
	CONSTRAINT uq_malla_asignatura_version_malla_id_asignatura_id UNIQUE (version_malla_id, asignatura_id), 
	CONSTRAINT uq_malla_asignatura_id_version_malla_id UNIQUE (id, version_malla_id), 
	CONSTRAINT ck_malla_asignatura_semestre_positivo CHECK (semestre_curricular > 0), 
	CONSTRAINT ck_malla_asignatura_regla_conocida CHECK (estado_regla IN ('ninguno_explicito_propuesto','prerrequisitos_asignaturas_propuestos','ninguno_identificado_sin_confirmar','prerrequisito_fuera_de_malla','depende_del_itinerario_no_definido','requisito_no_definido'))
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_0900_as_cs;


CREATE TABLE prerrequisito (
	version_malla_id INTEGER NOT NULL, 
	asignatura_id INTEGER NOT NULL, 
	requisito_asignatura_id INTEGER NOT NULL, 
	CONSTRAINT pk_prerrequisito PRIMARY KEY (version_malla_id, asignatura_id, requisito_asignatura_id), 
	CONSTRAINT ck_prerrequisito_no_autorreferencia CHECK (asignatura_id <> requisito_asignatura_id)
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_0900_as_cs;


CREATE TABLE usuario (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	correo_normalizado VARCHAR(254) NOT NULL, 
	creado_en DATETIME NOT NULL DEFAULT (UTC_TIMESTAMP()), 
	activo BOOL NOT NULL DEFAULT 1, 
	CONSTRAINT pk_usuario PRIMARY KEY (id), 
	CONSTRAINT uq_usuario_correo_normalizado UNIQUE (correo_normalizado)
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_0900_as_cs;


CREATE TABLE perfil_estudiante (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	usuario_id INTEGER NOT NULL, 
	CONSTRAINT pk_perfil_estudiante PRIMARY KEY (id), 
	CONSTRAINT uq_perfil_estudiante_usuario_id UNIQUE (usuario_id)
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_0900_as_cs;


CREATE TABLE revision_perfil (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	estudiante_id INTEGER NOT NULL, 
	numero INTEGER NOT NULL, 
	version_malla_id INTEGER NOT NULL, 
	semestre_declarado INTEGER NOT NULL, 
	creado_en DATETIME NOT NULL DEFAULT (UTC_TIMESTAMP()), 
	CONSTRAINT pk_revision_perfil PRIMARY KEY (id), 
	CONSTRAINT uq_revision_perfil_estudiante_id_numero UNIQUE (estudiante_id, numero), 
	CONSTRAINT uq_revision_perfil_estudiante_id_id UNIQUE (estudiante_id, id), 
	CONSTRAINT uq_revision_perfil_id_version_malla_id UNIQUE (id, version_malla_id), 
	CONSTRAINT ck_revision_perfil_numero_positivo CHECK (numero > 0), 
	CONSTRAINT ck_revision_perfil_semestre_positivo CHECK (semestre_declarado > 0)
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_0900_as_cs;


CREATE TABLE estado_academico_declarado (
	revision_perfil_id INTEGER NOT NULL, 
	malla_asignatura_id INTEGER NOT NULL, 
	version_malla_id INTEGER NOT NULL, 
	estado VARCHAR(16) NOT NULL, 
	CONSTRAINT pk_estado_academico_declarado PRIMARY KEY (revision_perfil_id, malla_asignatura_id), 
	CONSTRAINT ck_estado_academico_declarado_estado_valido CHECK (estado IN ('aprobada','reprobada','no_cursada'))
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_0900_as_cs;


CREATE TABLE rol (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	nombre VARCHAR(32) NOT NULL, 
	CONSTRAINT pk_rol PRIMARY KEY (id), 
	CONSTRAINT uq_rol_nombre UNIQUE (nombre)
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_0900_as_cs;


CREATE TABLE usuario_rol (
	usuario_id INTEGER NOT NULL, 
	rol_id INTEGER NOT NULL, 
	CONSTRAINT pk_usuario_rol PRIMARY KEY (usuario_id, rol_id)
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_0900_as_cs;


CREATE TABLE auth_control (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	CONSTRAINT pk_auth_control PRIMARY KEY (id)
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_0900_as_cs;


CREATE TABLE limite_auth (
	clave VARCHAR(64) NOT NULL, 
	ventana_en DATETIME NOT NULL, 
	ultimo_en DATETIME NOT NULL, 
	cantidad INTEGER NOT NULL, 
	CONSTRAINT pk_limite_auth PRIMARY KEY (clave)
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_0900_as_cs;


CREATE TABLE desafio_otp (
	id VARCHAR(64) NOT NULL, 
	correo_normalizado VARCHAR(254) NOT NULL, 
	proposito VARCHAR(16) NOT NULL, 
	codigo_digest VARCHAR(64) NOT NULL, 
	emitido_en DATETIME NOT NULL, 
	expira_en DATETIME NOT NULL, 
	consumido_en DATETIME, 
	invalidado_en DATETIME, 
	intentos INTEGER NOT NULL, 
	CONSTRAINT pk_desafio_otp PRIMARY KEY (id)
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_0900_as_cs;


CREATE TABLE sesion (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	usuario_id INTEGER NOT NULL, 
	token_digest VARCHAR(64) NOT NULL, 
	csrf_digest VARCHAR(64) NOT NULL, 
	creado_en DATETIME NOT NULL, 
	ultimo_en DATETIME NOT NULL, 
	expira_en DATETIME NOT NULL, 
	revocado_en DATETIME, 
	CONSTRAINT pk_sesion PRIMARY KEY (id), 
	CONSTRAINT uq_sesion_token_digest UNIQUE (token_digest)
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_0900_as_cs;


CREATE TABLE evento_seguridad (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	actor_usuario_id INTEGER, 
	tipo VARCHAR(40) NOT NULL, 
	instante DATETIME NOT NULL, 
	referencia_minima VARCHAR(64), 
	CONSTRAINT pk_evento_seguridad PRIMARY KEY (id)
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_0900_as_cs;


CREATE TABLE periodo_academico (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	identificador VARCHAR(64) NOT NULL, 
	inicio_periodo DATETIME, 
	captura_desde DATETIME NOT NULL, 
	captura_hasta DATETIME NOT NULL, 
	zona_horaria VARCHAR(64) NOT NULL, 
	estado_configuracion VARCHAR(16) NOT NULL DEFAULT 'borrador', 
	revision_control INTEGER NOT NULL DEFAULT '1', 
	CONSTRAINT pk_periodo_academico PRIMARY KEY (id), 
	CONSTRAINT ck_periodo_academico_orden_captura CHECK (captura_desde < captura_hasta), 
	CONSTRAINT ck_periodo_academico_captura_anterior_destino CHECK (inicio_periodo IS NULL OR captura_hasta < inicio_periodo), 
	CONSTRAINT ck_periodo_academico_estado_valido CHECK (estado_configuracion IN ('borrador','publicado')), 
	CONSTRAINT ck_periodo_academico_publicado_con_inicio CHECK (estado_configuracion = 'borrador' OR inicio_periodo IS NOT NULL), 
	CONSTRAINT ck_periodo_academico_revision_positiva CHECK (revision_control > 0), 
	CONSTRAINT uq_periodo_academico_identificador UNIQUE (identificador)
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_0900_as_cs;


CREATE TABLE planificacion_cupos (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	malla_asignatura_id INTEGER NOT NULL, 
	periodo_id INTEGER NOT NULL, 
	cupos_planificados INTEGER, 
	actualizado_en DATETIME NOT NULL DEFAULT (UTC_TIMESTAMP()), 
	responsable_usuario_id INTEGER, 
	CONSTRAINT pk_planificacion_cupos PRIMARY KEY (id), 
	CONSTRAINT uq_planificacion_cupos_malla_asignatura_id_periodo_id UNIQUE (malla_asignatura_id, periodo_id), 
	CONSTRAINT ck_planificacion_cupos_cupos_no_negativos CHECK (cupos_planificados >= 0)
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_0900_as_cs;


CREATE TABLE nota_administrativa (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	planificacion_id INTEGER NOT NULL, 
	autor_usuario_id INTEGER NOT NULL, 
	tipo VARCHAR(16) NOT NULL, 
	contenido TEXT NOT NULL, 
	creado_en DATETIME NOT NULL DEFAULT (UTC_TIMESTAMP()), 
	CONSTRAINT pk_nota_administrativa PRIMARY KEY (id), 
	CONSTRAINT ck_nota_administrativa_tipo_valido CHECK (tipo IN ('observacion','propuesta','decision')), 
	CONSTRAINT ck_nota_administrativa_contenido_no_vacio CHECK (CHAR_LENGTH(TRIM(contenido)) > 0)
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_0900_as_cs;


CREATE TABLE solicitud (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	estudiante_id INTEGER NOT NULL, 
	periodo_id INTEGER NOT NULL, 
	estado VARCHAR(16) NOT NULL DEFAULT 'borrador', 
	revision_control INTEGER NOT NULL DEFAULT '0', 
	version_trabajo_id INTEGER, 
	version_vigente_id INTEGER, 
	CONSTRAINT pk_solicitud PRIMARY KEY (id), 
	CONSTRAINT uq_solicitud_estudiante_id_periodo_id UNIQUE (estudiante_id, periodo_id), 
	CONSTRAINT uq_solicitud_id_estudiante_id UNIQUE (id, estudiante_id), 
	CONSTRAINT ck_solicitud_estado_h05b CHECK (estado IN ('borrador','enviada','invalidada')), 
	CONSTRAINT ck_solicitud_vigencia_h05b CHECK ((estado = 'enviada' AND version_vigente_id IS NOT NULL) OR (estado != 'enviada' AND version_vigente_id IS NULL)), 
	CONSTRAINT ck_solicitud_revision_no_negativa CHECK (revision_control >= 0)
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_0900_as_cs;


CREATE TABLE version_solicitud (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	solicitud_id INTEGER NOT NULL, 
	estudiante_id INTEGER NOT NULL, 
	numero INTEGER NOT NULL, 
	revision_perfil_id INTEGER NOT NULL, 
	version_malla_id INTEGER NOT NULL, 
	fundamento JSON, 
	creado_en DATETIME NOT NULL DEFAULT (UTC_TIMESTAMP()), 
	CONSTRAINT pk_version_solicitud PRIMARY KEY (id), 
	CONSTRAINT uq_version_solicitud_solicitud_id_numero UNIQUE (solicitud_id, numero), 
	CONSTRAINT uq_version_solicitud_solicitud_id_id UNIQUE (solicitud_id, id), 
	CONSTRAINT uq_version_solicitud_id_version_malla_id UNIQUE (id, version_malla_id), 
	CONSTRAINT ck_version_solicitud_numero_positivo CHECK (numero > 0)
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_0900_as_cs;


CREATE TABLE detalle_solicitud (
	version_id INTEGER NOT NULL, 
	malla_asignatura_id INTEGER NOT NULL, 
	version_malla_id INTEGER NOT NULL, 
	prioridad VARCHAR(8) NOT NULL, 
	CONSTRAINT pk_detalle_solicitud PRIMARY KEY (version_id, malla_asignatura_id), 
	CONSTRAINT ck_detalle_solicitud_prioridad_valida CHECK (prioridad IN ('alta','media','baja'))
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_0900_as_cs;


CREATE TABLE evento_solicitud (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	solicitud_id INTEGER NOT NULL, 
	version_id INTEGER NOT NULL, 
	tipo VARCHAR(24) NOT NULL, 
	creado_en DATETIME NOT NULL DEFAULT (UTC_TIMESTAMP()), 
	CONSTRAINT pk_evento_solicitud PRIMARY KEY (id)
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_0900_as_cs;


CREATE TABLE envio_idempotente (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	estudiante_id INTEGER NOT NULL, 
	periodo_id INTEGER NOT NULL, 
	clave VARCHAR(36) NOT NULL, 
	huella VARCHAR(64) NOT NULL, 
	respuesta JSON NOT NULL, 
	creado_en DATETIME NOT NULL DEFAULT (UTC_TIMESTAMP()), 
	CONSTRAINT pk_envio_idempotente PRIMARY KEY (id), 
	CONSTRAINT uq_envio_idempotente_estudiante_id_periodo_id_clave UNIQUE (estudiante_id, periodo_id, clave)
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_0900_as_cs;


-- Secondary indexes

CREATE INDEX ix_desafio_otp_correo_normalizado ON desafio_otp (correo_normalizado);

CREATE INDEX ix_planificacion_cupos_periodo_id ON planificacion_cupos (periodo_id);

CREATE INDEX ix_nota_administrativa_planificacion_fecha ON nota_administrativa (planificacion_id, creado_en, id);


-- Foreign keys (added after all referenced tables exist)

ALTER TABLE version_malla ADD CONSTRAINT fk_version_malla_carrera_id_carrera FOREIGN KEY(carrera_id) REFERENCES carrera (id) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE malla_asignatura ADD CONSTRAINT fk_malla_asignatura_asignatura_id_asignatura FOREIGN KEY(asignatura_id) REFERENCES asignatura (id) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE malla_asignatura ADD CONSTRAINT fk_malla_asignatura_version_malla_id_version_malla FOREIGN KEY(version_malla_id) REFERENCES version_malla (id) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE prerrequisito ADD CONSTRAINT fk_prerrequisito_version_malla_id_malla_asignatura FOREIGN KEY(version_malla_id, asignatura_id) REFERENCES malla_asignatura (version_malla_id, asignatura_id) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE prerrequisito ADD CONSTRAINT fk_prerrequisito_requisito FOREIGN KEY(version_malla_id, requisito_asignatura_id) REFERENCES malla_asignatura (version_malla_id, asignatura_id) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE perfil_estudiante ADD CONSTRAINT fk_perfil_estudiante_usuario_id_usuario FOREIGN KEY(usuario_id) REFERENCES usuario (id) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE revision_perfil ADD CONSTRAINT fk_revision_perfil_version_malla_id_version_malla FOREIGN KEY(version_malla_id) REFERENCES version_malla (id) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE revision_perfil ADD CONSTRAINT fk_revision_perfil_estudiante_id_perfil_estudiante FOREIGN KEY(estudiante_id) REFERENCES perfil_estudiante (id) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE estado_academico_declarado ADD CONSTRAINT fk_estado_entrada_malla FOREIGN KEY(malla_asignatura_id, version_malla_id) REFERENCES malla_asignatura (id, version_malla_id) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE estado_academico_declarado ADD CONSTRAINT fk_estado_academico_declarado_revision_perfil_id_revision_perfil FOREIGN KEY(revision_perfil_id, version_malla_id) REFERENCES revision_perfil (id, version_malla_id) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE usuario_rol ADD CONSTRAINT fk_usuario_rol_rol_id_rol FOREIGN KEY(rol_id) REFERENCES rol (id) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE usuario_rol ADD CONSTRAINT fk_usuario_rol_usuario_id_usuario FOREIGN KEY(usuario_id) REFERENCES usuario (id) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE sesion ADD CONSTRAINT fk_sesion_usuario_id_usuario FOREIGN KEY(usuario_id) REFERENCES usuario (id) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE evento_seguridad ADD CONSTRAINT fk_evento_seguridad_actor_usuario_id_usuario FOREIGN KEY(actor_usuario_id) REFERENCES usuario (id) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE planificacion_cupos ADD CONSTRAINT fk_planificacion_cupos_responsable_usuario_id_usuario FOREIGN KEY(responsable_usuario_id) REFERENCES usuario (id) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE planificacion_cupos ADD CONSTRAINT fk_planificacion_cupos_periodo_id_periodo_academico FOREIGN KEY(periodo_id) REFERENCES periodo_academico (id) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE planificacion_cupos ADD CONSTRAINT fk_planificacion_cupos_malla_asignatura_id_malla_asignatura FOREIGN KEY(malla_asignatura_id) REFERENCES malla_asignatura (id) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE nota_administrativa ADD CONSTRAINT fk_nota_administrativa_autor_usuario_id_usuario FOREIGN KEY(autor_usuario_id) REFERENCES usuario (id) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE nota_administrativa ADD CONSTRAINT fk_nota_administrativa_planificacion_id_planificacion_cupos FOREIGN KEY(planificacion_id) REFERENCES planificacion_cupos (id) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE solicitud ADD CONSTRAINT fk_solicitud_vigente FOREIGN KEY(id, version_vigente_id) REFERENCES version_solicitud (solicitud_id, id);

ALTER TABLE solicitud ADD CONSTRAINT fk_solicitud_trabajo FOREIGN KEY(id, version_trabajo_id) REFERENCES version_solicitud (solicitud_id, id);

ALTER TABLE solicitud ADD CONSTRAINT fk_solicitud_periodo_id_periodo_academico FOREIGN KEY(periodo_id) REFERENCES periodo_academico (id) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE solicitud ADD CONSTRAINT fk_solicitud_estudiante_id_perfil_estudiante FOREIGN KEY(estudiante_id) REFERENCES perfil_estudiante (id) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE version_solicitud ADD CONSTRAINT fk_version_solicitud_estudiante_id_revision_perfil FOREIGN KEY(estudiante_id, revision_perfil_id) REFERENCES revision_perfil (estudiante_id, id);

ALTER TABLE version_solicitud ADD CONSTRAINT fk_version_solicitud_solicitud_id_solicitud FOREIGN KEY(solicitud_id, estudiante_id) REFERENCES solicitud (id, estudiante_id);

ALTER TABLE version_solicitud ADD CONSTRAINT fk_version_solicitud_revision_perfil_id_revision_perfil FOREIGN KEY(revision_perfil_id, version_malla_id) REFERENCES revision_perfil (id, version_malla_id);

ALTER TABLE detalle_solicitud ADD CONSTRAINT fk_detalle_solicitud_version_id_version_solicitud FOREIGN KEY(version_id, version_malla_id) REFERENCES version_solicitud (id, version_malla_id);

ALTER TABLE detalle_solicitud ADD CONSTRAINT fk_detalle_solicitud_malla_asignatura_id_malla_asignatura FOREIGN KEY(malla_asignatura_id, version_malla_id) REFERENCES malla_asignatura (id, version_malla_id);

ALTER TABLE evento_solicitud ADD CONSTRAINT fk_evento_solicitud_solicitud_id_version_solicitud FOREIGN KEY(solicitud_id, version_id) REFERENCES version_solicitud (solicitud_id, id);

ALTER TABLE envio_idempotente ADD CONSTRAINT fk_envio_idempotente_estudiante_id_perfil_estudiante FOREIGN KEY(estudiante_id) REFERENCES perfil_estudiante (id) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE envio_idempotente ADD CONSTRAINT fk_envio_idempotente_periodo_id_periodo_academico FOREIGN KEY(periodo_id) REFERENCES periodo_academico (id) ON DELETE RESTRICT ON UPDATE RESTRICT;
