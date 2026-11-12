# H05-A — Selección y borrador local

## Alcance y decisiones

**Confirmado por la tarea:** selección propia desde la malla de la última revisión
académica; prioridades alta/media/baja (etiquetas ALTA/MEDIA/BAJA), máximo 3 altas,
4 medias+bajas y 7 total, sin compensación. Borrador vacío permitido. D03 se
revalida al guardar: aprobada, candidata sin declaración, prerrequisitos incumplidos
o reglas pendientes bloquean. La elegibilidad es autodeclarada y provisional.
No se usan cupos para habilitar o bloquear.

**Recomendado y adoptado para H05-A:** versiones de trabajo inmutables, revisión
esperada del perfil y principal, bloqueos perfil → período → principal dentro de
la transacción (precedidos por el bloqueo de identidad ya existente). Se usa
captura publicada en intervalo `[desde, hasta)`, reloj UTC del servidor. Una
solicitud principal por estudiante/período, garantizada también por UNIQUE.
No se sobrescriben versiones previas. La principal admite únicamente borrador en
este hito; la ampliación de estados y puntero vigente exige una futura migración.
La versión conserva FK a la revisión académica y versión de malla utilizadas.

**Pendiente y fuera de alcance:** envío, cierre como operación, eventos de envío,
reportes reales, administración, D04 para solicitudes enviadas, integración
institucional, cambio de malla y políticas institucionales. Las restricciones
históricas de documentos anteriores sobre solicitudes pendientes quedan
sustituidas exclusivamente para este borrador autorizado.

## Tablas y archivos

Reutilizadas: usuario, sesión, perfil_estudiante, revision_perfil,
estado_academico_declarado, version_malla, malla_asignatura, prerrequisito y
periodo_academico. No hay cambios a cupos.

Nuevas: `solicitud`, `version_solicitud`, `detalle_solicitud`. FK compuestas
aseguran dueño de revisión, pertenencia curricular del detalle y pertenencia del
puntero de trabajo a su principal. PK del detalle evita duplicados; CHECK valida
prioridad. Límites y elegibilidad se validan en FastAPI y Angular.

Migraciones aditivas `0004_h05a`, `0005_h05a`: la segunda corrige generación de
identidad con FK compuesta. En la primera prueba apareció falta de autoincremento;
MySQL exigió retirar/restablecer las FK nuevas para el ALTER. No se borraron filas,
no se reinicializó MySQL. El SQL de creación está congelado en la migración.

Código: `backend/app/drafts.py`, registro en `main.py`, tablas en `db/models.py`,
generador explícito `db/demo_period.py`, `tests/test_drafts.py`; componente
`features/academic/selection.*`, reglas `selection-rules.ts`, comprobador
`checks/selection.cjs` e integración en `demo.ts/html`. No se modificaron CSS,
cabecera estructural, menú ni pestañas. El botón superior deja de mostrar el
conteo ficticio del ejemplo. El selector lateral remite al período de Selección;
el estado lateral de estas dos rutas evita mostrar conteos del ejemplo.
Selección/Mi selección comparten el componente real.
Los cambios anteriores de H04-B/H04-C y otros archivos pendientes se conservaron.

## Contratos

Todos requieren sesión; respuestas sin caché, estudiante exclusivamente de sesión.

- `GET /api/v1/periods`: publicados y `captura_abierta`; sin fechas inventadas.
- `GET /api/v1/me/requests/{period_id}`: principal propia, revisión de control,
  `vigente: null`, trabajo con revisión académica, malla y selecciones. 404 si no
  existe. `?allow_empty=true` devuelve 200/null únicamente para ausencia de
  borrador, conservando errores de período/autenticación.
- `PUT /api/v1/me/requests/{period_id}/draft`: `revision_esperada` (0 inicial),
  `revision_perfil` (número actual), `selecciones` con `malla_asignatura_id` y
  `prioridad` en minúsculas. Reemplaza la colección mediante una nueva versión;
  devuelve la principal y trabajo persistidos.

Escrituras con origen autorizado y CSRF. 401 sesión ausente; 403 CSRF/origen o
cuenta no estudiantil; 409 revisión obsoleta/captura cerrada; 422 colección,
prioridad, duplicado, malla o elegibilidad inválidos. No se acepta estudiante ni
estado desde cliente. Un fallo de inserción revierte principal, versión y detalles.
El bloqueo compartido con el guardado del perfil serializa cambios académicos.

## Operación local y Firefox

Desde la raíz, con `.env` local ya configurado (no mostrar sus secretos):

```bash
docker compose up -d mysql mailpit
set -a
source .env
set +a
cd backend
.venv/bin/alembic upgrade head
# Solo si no existe período publicado con captura abierta:
.venv/bin/python -m app.db.demo_period
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

En otra terminal:

```bash
cd frontend
npm start
```

El generador crea, como máximo, un período `DEMOSTRACION-H05A-AAAAMMDD` por día
UTC, con ventana sintética relativa de siete días y destino posterior. Reejecutar
no modifica ni reabre el existente; no cambia períodos previos ni cupos. No se
invoca automáticamente en arranque ni desde el navegador.

1. En Firefox abrir `http://127.0.0.1:4200/iniciar-sesion`. Usar una cuenta
   sintética del dominio permitido en `.env`; obtener OTP en
   `http://127.0.0.1:8025` y verificarlo.
2. En **Perfil académico**, declarar NO CURSADA en una asignatura sin
   prerrequisitos y con regla verificable; guardar perfil. Mantener otra sin
   declaración para comprobar D03. No asumir habilitación por semestre.
3. Abrir **Selección** (`/seleccion`), elegir el período abierto. Solo se muestran
   asignaturas de la malla propia. Comprobar que la candidata sin declaración
   está bloqueada; agregar una habilitada, elegir ALTA/MEDIA/BAJA en el resumen.
4. Pulsar **Guardar borrador**; esperar «Borrador guardado». En Red de las
   herramientas de Firefox comprobar PUT 200, seguido de GET tras recargar.
5. Recargar: conserva selección, prioridad y revisión desde API/MySQL. Cerrar
   sesión e ingresar con la misma cuenta/OTP nuevo: **Mi selección** recupera el
   mismo período y borrador. No hay fuente de verdad en localStorage.
6. Cambiar prioridad o quitar materia, guardar: aumenta revisión conservando
   ID de principal. Se admite guardar vacío. Un cambio de período o recarga
   descarta cambios sin guardar, como indica la pantalla.
7. Abrir dos pestañas con la misma revisión; guardar en una y después en otra:
   la segunda muestra conflicto. Recargar explícitamente para recuperar el
   estado guardado antes de editar de nuevo. No hay sobrescritura silenciosa.

Un cambio posterior del perfil puede bloquear materias de un borrador recuperado.
Se conservan para permitir quitarlas, pero el backend exige corregir toda la
selección antes del siguiente guardado. No se envían ni cuentan como demanda.

## Evidencia

- `PREVIA_TEST_MYSQL=1 .venv/bin/pytest -q --tb=short`: **53 passed** sobre MySQL
  real, sin exclusiones; aviso existente de deprecación TestClient/httpx.
  Incluye OTP, perfil, D03, planificación y nuevos casos de guardado, modificación,
  historial inmutable, recuperación tras logout/login, aislamiento, autenticación,
  CSRF/origen, prioridades, duplicados, rollback y captura cerrada. Dos conexiones
  simultáneas: un 200 y un 409 al crear y al actualizar; una principal.
- `.venv/bin/alembic check`: sin operaciones pendientes.
- `.venv/bin/ruff check .`: aprobado en todo el backend.
- `git diff --check`: aprobado; Prettier de los tres archivos nuevos: aprobado.
- Frontend: `npm run build`: aprobado, sin advertencias; compilación de reglas a `/tmp/previa-h05a` y
  `node checks/selection.cjs` (10 comprobaciones); comprobador existente de
  Demanda con su compilación previa a `/tmp/previa-h01-c`.
- Revisión manual de Firefox **pendiente**: los pasos anteriores son una guía,
  no una afirmación de prueba visual ejecutada en esta entrega.
