# Primera tarea para Codex — Fase 0 (solo documentación)

Actúa como arquitecto de software y analista de requisitos para PREVIA, un sistema web nuevo de recopilación de demanda académica anticipada. Trabajarás en este repositorio **desde cero**.

Lee y respeta `AGENTS.md`, `docs/requirements.md`, `docs/decisions.md`, `docs/architecture.md` y `docs/roadmap.md`.

**Tarea actual:** completar la planificación técnica, NO implementar la aplicación.

1. Revisa los requisitos y detecta contradicciones, omisiones, decisiones que afectan al modelo de datos y riesgos de seguridad o conteo de demanda. No asumas hechos académicos no proporcionados.
2. Propón un esquema relacional normalizado para MySQL con entidades, claves, relaciones, restricciones de unicidad, versiones de intención, controles por período y justificación de las decisiones.
3. Diseña una máquina de estados para borrador, envío, actualización, retiro y cierre; explica cómo evitar duplicados y manejar los cambios de historial académico.
4. Propón el flujo seguro de autenticación por correo institucional + OTP (incluyendo entorno local con correo simulado), perfiles y autorización administrativa.
5. Diseña la estrategia para evaluar prerrequisitos declarados (sin afirmar elegibilidad oficial), prioridades 3+4 y reglas de reporte.
6. Propón un mapa de API REST y contratos mínimos de entrada/salida, sin generar backend.
7. Divide el desarrollo en hitos pequeños, ordenados, cada uno con pruebas y criterios de aceptación. Indica qué decisiones necesitan mi aprobación previa.
8. Actualiza documentos de planificación dentro de `docs/` y crea `docs/data-model.md`, `docs/api-design.md`, `docs/test-plan.md` si lo consideras útil. Mantén separados requisitos confirmados, recomendaciones y puntos pendientes.

**Restricciones estrictas:**
- No generes componentes Angular, endpoints ejecutables, modelos SQLAlchemy, docker-compose ni archivos de aplicación todavía.
- No instales paquetes, no arranques servicios, no crees commits y no hagas push.
- No inventes el dominio de correo, la carrera, la malla, los códigos de materias ni el calendario académico.
- No incorpores reconfirmación en v1.
- Al terminar, muestra una tabla de decisiones pendientes ordenada por impacto y explica qué archivos cambiaste.
