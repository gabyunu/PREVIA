# PREVIA — Plan incremental revisado en fase 0

## Alcance vigente H07 — Historial real

**Confirmado y autorizado:** consulta propia autenticada del historial MySQL por
período, con paginación de solicitudes y versiones, detalle de prioridades,
semestres, fechas, eventos y vigencia. Reutiliza tablas e instantáneas H05; no
modifica OTP, prerrequisitos, Demanda, envío ni vigencia. Sin retiro ni
reconfirmación. Véase [contrato y evidencia H07](h07-history.md).
La denominación H07 de esta entrega sustituye solo la numeración del plan antiguo
que llamaba H07 a revalidación; no autoriza otro alcance.
**Recomendado y adoptado:** lectura de 10 registros por página (máximo API 50),
creación de principal inferida de su primera versión existente.
**Pendiente:** políticas institucionales y revisión visual manual en Firefox.


## Alcance vigente H06

**Confirmado y autorizado:** Demanda y CSV administrativos desde solicitudes
persistidas enviadas y vigentes; separación por período/malla, cupos NULL/cero y
fixture H01-C independiente. Alta administrativa local explícita y auditada, sin
promoción pública ni cambios a OTP o D03/D04. Sustituye las restricciones históricas
sobre reportes pendientes solo para este alcance. Contrato, límites, verificaciones
y guía Firefox en [h06-demand.md](h06-demand.md). Políticas institucionales y
recorrido visual manual siguen **pendientes**.

## Alcance vigente H05-B

**Confirmado y autorizado:** envío definitivo propio, consulta y correcciones
durante captura conforme a D01/D04; versiones y fundamento históricos conservados.
Idempotencia transaccional adoptada para el piloto. Véase
[h05-b-submit.md](h05-b-submit.md). Sustituye las restricciones históricas de
H05-A para este alcance; reportes, retiro/recuperación y políticas institucionales
siguen pendientes.

## Alcance vigente H05-A

**Confirmado y autorizado:** selección y borrador propio persistido, sin envío ni
reportes reales. Esta ampliación sustituye las restricciones históricas solo para
H05-A. Contratos, mecanismos adoptados, evidencia y pendientes en
[h05-a-drafts.md](h05-a-drafts.md). D03 y límites independientes se conservan.

## Alcance vigente H04-B y ratificación D03

**Confirmado:** consulta de elegibilidad curricular autodeclarada y provisional
con la última revisión propia. APROBADA no es seleccionable; REPROBADA y
NO CURSADA requieren todos los prerrequisitos APROBADA y reglas suficientemente
verificadas. Una candidata sin declaración permanece bloqueada aunque cumpla
los prerrequisitos. «Prerrequisitos cumplidos» y «habilitada para selección»
son resultados distintos. Véase [contrato y evidencia H04-B](h04-b-eligibility.md).
Este alcance sustituye las menciones históricas a elegibilidad pendiente.
Solicitudes, cambios de malla y certificación institucional siguen fuera de alcance.


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

**Confirmado**: desarrollo por fases, local, con revisión al terminar cada fase.
**Recomendado**: desglose siguiente. **Pendiente**: autorizar inicio de fase 1 y adoptar su configuración técnica mínima
(planning-review.md); resolver pendientes D07–D13 antes de los hitos afectados.
D01–D06 ya están confirmadas funcionalmente. Una revisión documental
completa no autoriza avanzar automáticamente. No trabajar todas las fases a la vez.

## Estado de ejecución

H01 fue autorizado por el usuario y se implementó de forma local con Angular 22
y Python 3.14. Véase [evidencia de H01](h01-verification.md). Esta autorización
reemplaza la pendiente de inicio únicamente para H01. H02 y los demás hitos
siguen pendientes de autorización; la fase 1 completa no está cerrada.

H01-B fue autorizado específicamente para migrar la referencia visual anterior
a Angular 22. Se implementaron cinco vistas de demostración con datos sintéticos
y estado en memoria, sin integración API ni persistencia. Véase la
[entrega H01-B](h01-b-migration.md), incluida la revisión visual manual pendiente.
Esto no autoriza H02 ni las funcionalidades de los hitos posteriores.

## H02-A — autorización específica y entrega

El usuario autorizó H02-A: MySQL local, SQLAlchemy/Alembic, tablas base de catálogo
y perfiles y carga de las 53 asignaturas provisionales. Esta subdivisión incorpora
únicamente persistencia inicial de las áreas H03/H04; no autoriza sus servicios,
APIs ni evaluador, tampoco H02-B ni autenticación. Véase
[operación y evidencia H02-A](h02-a-persistence.md). Las referencias anteriores a
H02 pendiente se conservan como contexto de la planificación original; la autorización
actual se limita a H02-A. La fase 1 completa no está cerrada.

## Fase 0 — Documentación y diseño

Entregables: requirements.md y decisions.md con estatus explícito; planning-review.md,
architecture.md, data-model.md, api-design.md, test-plan.md y este plan.
Aceptación: sin contradicciones críticas ocultas; recomendaciones y pendientes
identificadas; esquema, contratos, transiciones y pruebas revisables. Solo docs/.

## Hitos propuestos por dependencia

Cada fila es una entrega revisable. D01–D06 en dependencias son reglas ya
confirmadas; D07–D13 distinguen recomendaciones locales y pendientes por hito en planning-review.md. Los mecanismos siguen propuestos. Las rutas futuras indican áreas previstas, no
archivos creados ni una estructura definitiva aprobada. Cada tarea respeta el
alcance de su fase y registra evidencia según test-plan.md.

| Fase / hito | Dependencia y aprobación previa | Archivos/área previstos y comportamiento | Prueba y criterio de aceptación | Límite |
|---|---|---|---|---|
| 1 / H01 Esqueleto | Revisión fase 0; herramientas D12 | backend/, frontend/, documentación local: Angular/FastAPI y /health | Compilación frontend, health y Ruff/pytest mínimos; arranque documentado | Sin reglas académicas ni datos reales |
| 1 / H02 Persistencia local | H01; MySQL/Alembic/Mailpit D12 | Migraciones base, Compose y .env.example ficticio | MySQL inicia, migración aplica, datos sintéticos persisten al reiniciar | Sin SMTP externo ni despliegue |
| 2 / H03 Catálogo versionado | Revisión fase 1, H02; D07/D11 y catálogo sintético acordado | Migraciones catálogo, validación de grafo/importación local | FK, unicidades, ciclos, versiones y persistencia verificadas | Sin inventar malla oficial ni equivalencias |
| 2 / H04 Perfil y evaluador | H03; D03/D05/D11 | Revisiones académicas y servicio puro de reglas | Matriz de prerequisitos y estados, mallas ajenas rechazadas | Sin API pública sin autenticación; datos sintéticos |
| 3 / H05 Identidad | Revisión fase 2; D08/D09/D10/D12 | OTP, sesión, permisos y correo simulado | Código único bajo concurrencia, límites compartidos, roles y CSRF probados | Sin SMTP real, admin no autoregistrable |
| 3 / H06 Solicitudes | H04/H05; D01/D02/D06 | Principal/versiones, eventos, API de captura | Prioridades, estados, límites temporales, dueños y carreras concurrentes verificados | Sin reconfirmación ni excepciones no aprobadas |
| 3 / H07 Revalidación | H06; D04/D11 | Actualización de perfil y vigencia transaccional | Cambio incompatible no deja demanda vigente; cierre conserva instantánea | Sin corrección histórica implícita |
| 4 / H08 Acceso y perfil Angular | Revisión fase 3; H05/H07 | frontend/: acceso, perfil y malla con causas | Interfaz conectada, errores/sesión y estados desconocidos claros | Backend sigue siendo autoridad |
| 4 / H09 Selección Angular | H08/H06 | frontend/: prioridades, borrador, envío, retiro/recuperación | Flujo API y conflictos visibles; guardar no equivale a enviar | Sin matrícula, cupos u horarios |
| 5 / H10 Reporte y CSV | Revisión fase 4; H07, D01/D10/D13 | Consultas agregadas, API y vista administrativa | Conteos exactos de fixture sintético, permisos y CSV seguro | Sin tasas institucionales ni capacidad ficticia |
| 5 / H11 Integración y operación | H10 y H09 | Pruebas integrales y guía local | Flujo completo y reinicio conservan datos; comandos/resultados documentados | Sin despliegue ni secretos reales |

Si un hito resulta grande, subdividirlo por migración, servicio, API y vista,
cada uno con su aceptación, sin abrir la siguiente fase antes de revisión.

## Puertas de revisión

- Fase 1: arranque local reproducible, sin datos reales ni secretos en Git.
- Fase 2: modelo y evaluador aprobados; esquema y persistencia comprobados en MySQL.
- Fase 3: controles de backend efectivos; ningún usuario opera solicitudes ajenas;
  no se reporta versión incompatible y se conserva historial.
- Fase 4: flujos conectados y fallos explicados sin inventar resultados académicos.
- Fase 5: reportes correctos, CSV agregado y persistencia integral probada.

## Próxima revisión recomendada

No hay información institucional pendiente que bloquee H01/H02 sintéticos.
La primera tarea recomendada es H01, con alcance y aceptación de la tabla; H02
sigue tras su verificación. Esta revisión no autoriza programarlos.

D01–D06 fijan ya la semántica funcional del modelo. Revisar catálogo,
identidad, acceso y privacidad D07–D13 antes de programar cada área. La falta de malla
real permite diseñar fixtures sintéticos etiquetados cuando se autorice la fase
correspondiente; no permite afirmar integración o reglas institucionales reales.
