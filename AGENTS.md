# Instrucciones para Codex — PREVIA

## Propósito
PREVIA recoge, al final de un semestre, las materias que estudiantes desean cursar en el siguiente período y produce reportes de demanda académica declarada. No realiza matrícula, reserva cupos ni asigna horarios/paralelos.

## Fuente de verdad
Lee `docs/requirements.md`, `docs/decisions.md`, `docs/architecture.md` y `docs/roadmap.md` antes de proponer o implementar cambios. Distingue siempre **confirmado**, **recomendado** y **pendiente**. Nunca conviertas una decisión pendiente en una regla definitiva silenciosamente.

## Alcance y arquitectura
- Repositorio nuevo; no reutilizar código de prototipos previos sin aprobación explícita.
- Frontend: Angular + TypeScript.
- Backend: Python + FastAPI + Pydantic + SQLAlchemy.
- Base de datos: MySQL; contenedores Docker Compose en desarrollo.
- Pruebas: pytest y herramientas de verificación adecuadas al frontend; análisis estático con Ruff.
- Autenticación prevista: correo de dominio institucional autorizado + OTP, sin contraseñas estudiantiles y sin Google OAuth.
- Primera versión ejecutable localmente, con datos sintéticos y/o públicos autorizados. Nada de datos privados reales ni despliegue por defecto.

## Reglas de trabajo
1. Trabaja por fases y entrega cambios pequeños, comprobables y revisables.
2. Antes de programar, explica alcance, dependencias, riesgos y criterios de aceptación de la tarea.
3. En la fase 0 modifica únicamente documentación. No instales dependencias ni generes código aplicativo.
4. Nunca simules que ejecutaste una prueba; indica comando, resultado y limitaciones reales.
5. No hagas commits, push, despliegues, llamadas a servicios externos ni operaciones destructivas sin permiso explícito.
6. Mantén secretos fuera de Git; usa `.env.example` con valores ficticios cuando corresponda.
7. Valida en backend permisos, estados de solicitud, límites de selección y prerrequisitos. El frontend no constituye un control de seguridad.
8. No inventes carreras, mallas curriculares, prerrequisitos, fechas o dominios institucionales; usa datos de demostración etiquetados o declara el bloqueo.
9. Reporta contradicciones y decisiones pendientes antes de implementarlas.
10. Al terminar una fase, incluye resumen de archivos modificados, verificaciones ejecutadas y pendientes.

## D03 confirmada — H04-B
- APROBADA nunca es seleccionable de nuevo.
- REPROBADA y NO CURSADA solo son seleccionables con todos sus prerrequisitos
  declarados APROBADA y reglas suficientemente verificadas.
- Sin declaración de la candidata: bloquear con un motivo claro hasta declarar
  su estado, aunque sus prerrequisitos estén cumplidos.
- Prerrequisitos incumplidos, desconocidos o pendientes de verificación bloquean.
- Distinguir «prerrequisitos cumplidos» de «asignatura habilitada para selección».
  Ausencia de declaración nunca equivale a NO CURSADA ni a APROBADA.
- La elegibilidad es autodeclarada y provisional, sin certificación universitaria.
