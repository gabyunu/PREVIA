# PREVIA — Arquitectura objetivo preliminar

> Documento de orientación. Codex debe revisarlo y proponer decisiones técnicas sin implementar código durante la fase 0.

## Stack
- **Frontend**: Angular y TypeScript.
- **API**: FastAPI + Pydantic.
- **Persistencia**: SQLAlchemy y MySQL, con migraciones versionadas (proponer herramienta concreta).
- **Desarrollo**: Docker Compose para servicios reproducibles, incluyendo servidor de correo de prueba.
- **Pruebas**: pytest (backend), pruebas de frontend y de integración; Ruff (Python).
- **Control de versiones**: Git + GitHub cuando se decida subir el repositorio.

## Responsabilidades
Frontend -> API HTTP -> servicios de dominio -> capa de persistencia -> MySQL.

El backend centraliza controles de autenticación/sesión, permisos por rol, restricciones por prerrequisitos, límites de selección, ciclo de vida, transacciones y reportes. La interfaz replica validaciones para una mejor experiencia, pero jamás es fuente única de autorización.

## Entidades candidatas (no esquema aprobado)
Usuario, PerfilEstudiante, Carrera, VersionMalla, Asignatura, MallaAsignatura, Prerrequisito, PeriodoAcademico, EstadoAcademicoDeclarado, Solicitud, DetalleSolicitud, VersionSolicitud/EventoAuditoria, CodigoVerificacion o RegistroOTP, Sesion.

Debemos decidir cardinalidades, tablas normalizadas, unicidades, claves foráneas, índices, migraciones, política de OTP y auditoría antes de generar modelos.

## Riesgos técnicos
- Incorrección en conteos por versiones/retiradas.
- Permitir selección no elegible por una validación hecha solo en frontend.
- Suplantación por correo no institucional o por OTP sin controles adecuados.
- Datos académicos autodeclarados confundidos con información oficial.
- Una única malla para cohortes distintas.
- Manejo incompleto de campos sin calificación disponible.
