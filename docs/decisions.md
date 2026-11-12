# PREVIA — Registro de decisiones (v0.6)

## Alcance vigente H04-A

**Confirmado y autorizado:** perfil académico propio con sesión OTP, catálogo de las
53 asignaturas del piloto, estados autodeclarados y revisiones completas en MySQL.
Esta autorización sustituye las restricciones históricas de implementación
únicamente para H04-A. Véase [contrato, verificación y demostración](h04-a-academic-profile.md).
**Recomendado y adoptado localmente:** control de revisión esperada y bloqueo del
perfil; lectura excepcional del borrador piloto sin publicarlo.
**Pendiente:** D11 para cambios de carrera/malla, fuentes oficiales, privacidad
institucional, elegibilidad, solicitudes, administración y reportes persistidos.
No se amplía el alcance a esos servicios.


## Alcance específico H02-C

**Confirmado e implementado:** persistencia aditiva de períodos, planificación de
cupos y notas administrativas, más fuente/fecha de revisión de reglas curriculares.
La autorización actual se limita a H02-C y conserva H02-A/H02-B; las menciones
históricas a fase 0 o autorización pendiente no describen esta entrega.
Véanse [tablas, límites, reportes futuros y evidencia H02-C](h02-c-planning.md).
Cupos orientativos no constituyen oferta ni condicionan selección; NULL o ausencia
significa desconocido, cero es explícito. Sin nuevas APIs ni cambios visuales,
de autenticación o de las 53 asignaturas. Solicitudes y reportes reales siguen
**pendientes**, al igual que servicios administrativos y datos institucionales.

## Estado de implementación H02-B

El usuario autorizó autenticación **solo local** con OTP, Mailpit, sesiones y
conexión Angular. Está implementada y verificada según
[alcance, configuración y evidencia H02-B](h02-b-authentication.md).
Las notas históricas sobre fase 0, ausencia de endpoints o H02-B pendiente se
limitan al estado anterior. No se autoriza perfil académico ni hitos posteriores.
Los dominios oficiales, privacidad/retención y administración siguen pendientes.

## Confirmado por el alcance acordado
- Se desarrolla una versión nueva **desde cero**.
- Se usará al cierre del semestre para declarar interés de materias para el siguiente período.
- Es un sistema de retroalimentación para planificación, no una continuación del trámite de matrícula oficial.
- Ejecución local en v1.
- Angular, FastAPI, SQLAlchemy, MySQL y Docker como tecnologías previstas.
- Estados académicos declarados que verá el estudiante: aprobada, reprobada, no cursada.
- La malla debe ser visible e incluir relaciones de prerrequisitos.
- Se bloqueará la selección de asignaturas sin prerrequisitos declarados cumplidos.
- Hasta tres asignaturas altas y cuatro adicionales medias/bajas.
- La reconfirmación no estará en v1 por falta de tiempo; reconsiderable en el futuro.
- Se inicia sesión mediante control de correo de dominio institucional y OTP, sin integración con Google OAuth ni el sistema oficial.
- No se calcula participación de toda la institución sin padrón; eventual análisis entre períodos posteriores.

## Decisiones funcionales confirmadas en esta revisión

| ID | Decisión aprobada |
|---|---|
| D01 | Borradores excluidos; edición, retiro y recuperación durante captura; historial conservado; solo cuenta la última versión enviada y vigente. Exportación de reportes agregados en CSV. |
| D02 | Envío con al menos una materia de cualquier prioridad; hasta tres altas y cuatro adicionales medias/bajas. No se exige ninguna alta. |
| D03 | Exactamente aprobada, reprobada y no cursada como estados académicos visibles. Ausencia significa desconocido, sin equivalencia automática. Selección exige estado conocido y todos los prerrequisitos declarados aprobados. |
| D04 | Cambio incompatible del historial excluye inmediatamente toda la solicitud enviada de la demanda vigente, conservando historial y requiriendo corrección y nuevo envío. Operaciones transaccionales; instantánea histórica preservada después del cierre. |
| D05 | Cualquier asignatura pendiente de la malla correspondiente con prerrequisitos cumplidos puede seleccionarse. Sin catálogo independiente de oferta por período en v1; interés potencial, no disponibilidad confirmada. |
| D06 | Período identifica semestre destino; ventana anterior configurable, instantes UTC y zona IANA configurable; sin reaperturas excepcionales en v1. |

## Consolidación técnica para inicio local

**Confirmado en esta revisión:** OTP válido inicia sesión si la cuenta existe;
primer acceso crea cuenta de estudiante. Administradores únicamente por procedimiento
controlado, nunca registro público ni rol indicado por cliente. Se mantienen límites,
seguridad de sesiones y suspensión de cuentas. Cambios de historial solo invalidan
solicitudes con captura abierta; solicitudes cerradas conservan su fundamento histórico.

**Recomendado y listo para desarrollo local tras autorización:** idempotencia de
submit con clave por usuario/período y resultado transaccional; campo `inicio_periodo`
y validación de captura anterior; mallas publicadas inmutables; agregación separada
por versión/entrada curricular, prioridad, semestres y repetición declarada. Véanse
contratos y modelo. No se incorporan equivalencias automáticas entre mallas.

D07–D13 tienen configuración mínima recomendada y bloqueos por hito en
[planning-review.md](planning-review.md). Los datos institucionales siguen
**pendientes**: dominios reales, fuentes curriculares y fechas autorizadas, además
de privacidad/retención antes de datos reales. No bloquean H01/H02 sintéticos.
Herramientas y parámetros técnicos siguen siendo propuestas, sin implementación.

## No afirmar
- Que la verificación por correo certifica matrícula activa.
- Que la información declarada permite elegibilidad oficial.
- Que se conoce la demanda de toda la institución.
- Que existen fechas, mallas o datos académicos oficiales autorizados si no se han proporcionado.

## Alcance de la aprobación

D01–D06 aprueban comportamiento funcional, incluidas atomicidad e instantánea al cierre.
Los diseños de tablas, revisiones inmutables, punteros, estados internos, bloqueos,
contratos REST, límites exactos de ventana, congelación de configuración al publicar,
Alembic, Mailpit y parámetros OTP/sesión siguen siendo recomendaciones técnicas.
D11 mantiene pendientes cambios de carrera/malla y correcciones históricas; la propuesta local los excluye y conserva publicaciones inmutables; no reabre D04.
D13 dispone de definición técnica recomendada para repetición y separación por malla; detalles institucionales siguen pendientes y no reabren el CSV agregado de D01.

Diseños relacionados: [modelo](data-model.md), [arquitectura](architecture.md),
[API](api-design.md), [pruebas](test-plan.md) y [hitos](roadmap.md).
Se mantiene fase 0 documental, sin autorización de código, instalaciones, commits,
push, despliegues ni servicios externos.
