# PREVIA — Revisión de fase 0

## Alcance y aceptación

Revisión documental de AGENTS.md, requirements.md, decisions.md, architecture.md,
roadmap.md y prompts/01_planificacion.md. No autoriza implementar la fase 1.
No se han aportado dominio institucional, carrera, malla ni calendario oficial.

**Confirmado**: alcance local, tecnologías acordadas, autodeclaración, bloqueo por
prerrequisitos, prohibición de elegir aprobadas, prioridades hasta 3 altas y 4
medias/bajas (7 total), OTP institucional sin contraseña ni Google OAuth, sin
reconfirmación ni matrícula. Los controles corresponden al backend.

**Recomendado**: todos los diseños técnicos nuevos de esta fase, incluidos tablas,
contratos, transacciones, estados internos, herramientas y parámetros operativos.
**Pendiente**: adopción de recomendaciones técnicas al autorizar implementación y datos institucionales según la tabla D07–D13.
Los ejemplos describen estructura; no representan datos académicos reales.

Aceptación documental: decisiones abiertas visibles, propuesta relacional trazable,
transiciones y conteos definidos, contratos revisables y tareas con verificaciones.
La coherencia documental no equivale a aprobar las propuestas ni a validar software.

## Consolidación D01–D06

D01–D06 están **confirmadas** con el alcance registrado en decisions.md y requirements.md.
Los mecanismos técnicos continúan **recomendados**; D07–D13 se consolidan abajo con pendientes por hito.
La aprobación no autoriza iniciar implementación ni fija datos institucionales.

| ID | Decisión funcional confirmada |
|---|---|
| D01 | Solo última versión enviada y vigente cuenta; borradores excluidos; edición, retiro, recuperación e historial durante captura; CSV agregado. |
| D02 | Mínimo una asignatura de cualquier prioridad; hasta 3 altas y 4 medias/bajas; altas opcionales. |
| D03 | Tres estados visibles; ausencia desconocida; candidata con estado conocido y todos los prerrequisitos declarados aprobados. |
| D04 | Cambio incompatible del historial excluye toda la solicitud inmediatamente y transaccionalmente; historial, corrección y nuevo envío; instantánea preservada tras cierre. |
| D05 | Selección de pendientes de la malla con prerrequisitos; sin oferta independiente por período; interés potencial. |
| D06 | Período destino con ventana anterior configurable, UTC y zona IANA configurable; sin reaperturas excepcionales en v1. |

## Consolidación D07–D13 para desarrollo local

Esta revisión confirma el flujo OTP de acceso/creación de estudiante y el alta
administrativa controlada, así como la limitación de D04 a captura abierta.
**Recomendado, listo para adoptar al autorizar la tarea correspondiente:** la
configuración mínima siguiente. No supone aprobación institucional ni autorización
de código en esta fase. Los mecanismos del modelo y API conservan estatus de propuesta.

| ID | Configuración mínima recomendada | Pendiente y bloqueo real |
|---|---|---|
| D07 | Fixtures sintéticos etiquetados; malla versionada, prerrequisitos AND; sin equivalencias ni correquisitos | Fuente y reglas oficiales bloquean importación real, no H01/H02 |
| D08 | Lista exacta configurable; correos sintéticos bajo un dominio reservado de pruebas, sin entrega externa. Quitar espacios externos, normalizar dominio a minúsculas y preservar parte local; aplicar misma regla a UNIQUE, OTP y alta controlada | Dominios autorizados y política institucional de correo bloquean acceso real; no desarrollo local |
| D09 | Cuenta administrativa sintética creada/asignada por comando local explícito de operador autorizado y auditado, sin endpoint público; login OTP con los mismos controles; no confiar en rol del cliente | Identidad y autorización del operador real antes de administración con datos reales. Procedimiento local se implementa en H05, no bloquea H01/H02 |
| D10 | Solo datos sintéticos, acceso mínimo, CSV agregado sin identificadores personales, sin datos sensibles en logs; conservar históricos y registros idempotentes durante las pruebas; no borrado automático ni retención infinita como política institucional | Aviso, base autorizada, plazos por clase de dato y tratamiento de grupos pequeños antes de datos reales; no H01/H02 |
| D11 | Publicaciones inmutables; una malla activa; rechazar cambios posteriores de carrera/malla por API ordinaria, sin migraciones ni traslado de aprobaciones. Historial solo revalida solicitudes en captura abierta | Cambios de carrera/malla y correcciones retrospectivas requieren decisión posterior; no se implementan en v1 local mínima |
| D12 | Compose con MySQL InnoDB y Mailpit aislados localmente; SQLAlchemy/Alembic, pytest/Ruff y herramientas Angular; sesiones opacas en BD y controles OTP compartidos | Versiones compatibles y comandos se seleccionan/verifican en H01/H02. Parámetros de seguridad siguientes son propuesta para H05, no bloqueo del esqueleto |
| D13 | Agregados por período, versión/entrada curricular, prioridad, semestres y repetición declarada; separar mallas, sin equivalencias inferidas; CSV UTF-8 protegido, mismos filtros/instantánea y sin datos personales | Diseño de consolidación entre versiones queda fuera de v1. Fuentes de capacidad y denominadores institucionales no disponibles; no se simulan |

Para D12 se recomienda ensayar los parámetros ya propuestos: OTP de 8 dígitos,
10 minutos, 5 intentos, 60 segundos entre emisiones y 5 emisiones/hora por correo;
límite adicional inicial configurable de 30 solicitudes/hora por IP, sin sustituir
el límite por correo. Sesión de 8 horas absolutas/30 minutos inactiva. Revisar con
pruebas sintéticas antes de H05; no son políticas institucionales confirmadas.
Mantener HMAC de OTP con secreto fuera de BD, rotación/revocación, CSRF, origen,
CORS restringido y cookies HttpOnly/SameSite; Secure bajo HTTPS, excepción HTTP
exclusivamente local. Mailpit no habilita OTP universal ni logs de códigos.

Configuración local mínima: backend y frontend en localhost, MySQL con volumen
persistente y BD de pruebas separada, Mailpit sin retransmisión externa; puertos,
lista de dominios, zona IANA, fechas, límites y secretos configurables. Credenciales
ficticias documentadas después en .env.example; secretos locales fuera de Git.
No se necesita SMTP externo, Google OAuth, infraestructura de producción ni datos
privados. No instalar ni crear esos artefactos durante esta revisión documental.

## Qué está listo y qué bloquea la fase 1

D01–D06, acceso OTP con creación de estudiante, administración controlada y
preservación de períodos cerrados están **confirmados**. Arquitectura general
mantenida. Modelo/API con idempotencia transaccional, `inicio_periodo`, revisiones,
publicaciones inmutables y separación de mallas en reportes quedan **recomendados**
y suficientemente definidos para tareas locales revisables.

**No hay dato institucional pendiente que bloquee H01/H02** usando solo datos
sintéticos. Falta autorizar expresamente el inicio de implementación: esta solicitud
es exclusivamente documental. La aceptación de herramientas/configuración técnica
mínima puede resolverse al autorizar H01/H02; las versiones concretas se fijarán allí,
sin afirmar compatibilidad antes de comprobarla. D07–D13 se revisan antes de los
hitos afectados, no como bloqueo global de toda la fase 1.

**Primera tarea recomendada: H01**, esqueleto local Angular/TypeScript y
FastAPI/Pydantic, ruta /health sin información sensible y guía de arranque; seleccionar
versiones compatibles, registrar compilación frontend, prueba de health y Ruff.
Sin reglas académicas, OTP real, migraciones de dominio ni servicios externos.
H02 añade Compose/MySQL, migración mínima y verificación de persistencia con datos
sintéticos. Requiere una nueva autorización de implementación, no se ejecuta ahora.

## Impacto y contradicciones revisadas

- **Modelo de datos:** D02 fija mínimo de envío, sin impedir borradores vacíos;
  D03 representa desconocido mediante ausencia, sin cuarto valor académico; D05
  descarta oferta_periodo en v1. Revisiones y punteros propuestos permiten D01/D04,
  pero deben excluir toda la solicitud incompatible de forma atómica y conservar
  su fundamento histórico tras cierre. No se detecta una contradicción estructural nueva.
- **API:** se eliminan mínimos condicionales y futuros contratos de oferta en v1.
  Actualizar historial y excluir solicitudes incompatibles constituye una sola operación;
  tras cierre no altera reportes históricos. Recuperar como borrador es una propuesta
  de contrato y requiere nuevo envío validado para volver a contar.
- **Pruebas:** envío vacío falla, una media o baja basta, 0+4 es válido y candidata
  sin declaración falla incluso sin prerrequisitos. Deben probarse exclusión total,
  rollback, concurrencia y estabilidad histórica; no hay pruebas ejecutables todavía.
- **Pendientes técnicos, no decisiones aprobadas:** intervalo [apertura, cierre),
  `inicio_periodo`, rechazo de horas ambiguas sin desplazamiento y congelación de configuración
  al publicar, ahora descritos en modelo y API. D06 confirma fechas configurables, no esa política de publicación.
- **Límite funcional conservado:** un prerrequisito todavía en curso/desconocido
  bloquea; no se autoriza aprobación futura o condicional. La instantánea histórica
  conserva autodeclaración, no certifica elegibilidad oficial. Retención sigue en D10.

## Mapa de entregables

requirements.md y decisions.md consolidan D01–D06; architecture.md, data-model.md,
api-design.md y test-plan.md alinean las propuestas técnicas con esas reglas.
roadmap.md distingue decisiones aprobadas de dependencias aún pendientes.
