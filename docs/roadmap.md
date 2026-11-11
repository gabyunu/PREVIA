# PREVIA — Plan incremental

## Fase 0 — Documentación y diseño (sin código aplicativo)
Entregables: especificación funcional depurada, decisiones pendientes, arquitectura, diagrama relacional propuesto, contratos de API preliminares, plan de pruebas y tareas pequeñas por orden de dependencia.
Aprobación: no quedan contradicciones críticas ocultas; decisiones abiertas están etiquetadas explícitamente.

## Fase 1 — Proyecto ejecutable
Entregables: esqueleto Angular/FastAPI, MySQL/Docker Compose, variables de entorno ejemplificadas, `/health`, pruebas mínimas, comandos de arranque.
Aprobación: servicios inician en local; sin datos reales ni secretos subidos a Git.

## Fase 2 — Datos y malla
Entregables: migraciones, catálogo/malla importable, versiones, prerrequisitos, estados académicos declarados, datos sintéticos.
Aprobación: restricciones, consultas y persistencia probadas.

## Fase 3 — Identidad y API
Entregables: OTP seguro y simulación de correo; roles y sesiones; solicitudes y validaciones; pruebas.
Aprobación: el servidor deniega operaciones entre cuentas y materias no elegibles.

## Fase 4 — Angular
Entregables: acceso por correo, perfil académico, malla navegable, selección priorizada, borradores y envíos, estados claros.
Aprobación: interfaz conectada a la API, maneja fallos y bloqueos.

## Fase 5 — Reportes, integración y calidad
Entregables: reportes por período/prioridad, CSV, pruebas de flujo integral, documentación de operación local.
Aprobación: no duplica demanda, excluye borradores/retiradas y sobrevive reinicios.

## Regla de ejecución
Cada fase requiere revisión antes de abrir la siguiente. No trabajar en todas a la vez. Cada tarea debe incluir archivos afectados, comportamiento esperado, pruebas y límites.
