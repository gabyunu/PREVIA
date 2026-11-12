# H05-B — Envío definitivo local

**Confirmado por la tarea:** envío propio de intención académica, sin matrícula ni
reserva de cupo; se conserva el diseño académico y todos los cambios anteriores.
Esta ampliación sustituye las restricciones históricas de H05-A solo para envío,
consulta y corrección documentada. No conecta Demanda ni modifica OTP,
prerrequisitos, cupos, calendario o datos oficiales.

**Recomendado y adoptado localmente:** contrato de idempotencia UUID de
api-design.md, bloqueos identidad → perfil → período → principal, revisiones
esperadas, evaluación en backend y transacción única. Las versiones son de solo
inserción desde los servicios: no se actualizan ni borran al editar o enviar.
No se afirma protección frente a un administrador con escritura directa en MySQL.

**Confirmado D01/D04:** guardar una corrección mantiene vigente el envío anterior;
enviar la corrección sustituye únicamente el puntero vigente y conserva versiones.
Un cambio académico incompatible invalida toda la solicitud en captura abierta;
un cambio compatible crea una versión equivalente con fundamento nuevo sin tocar
el trabajo pendiente. Tras cierre no se recalcula ni modifica el envío histórico.
No se añaden retiro, recuperación, historial paginado ni reportes en este hito.

## API y persistencia

`POST /api/v1/me/requests/{period_id}/submit`, sesión propia, origen permitido,
CSRF y `Idempotency-Key: <UUID>`. Cuerpo estricto:

```json
{"revision_esperada": 1, "version_trabajo_id": 1, "revision_perfil": 1}
```

Devuelve 200 con principal, revisión, `estado: enviada`, `version_vigente_id`,
`vigente` y `trabajo: null`. GET propio devuelve la misma estructura actual;
las selecciones incluyen nombre y semestre curricular. PUT draft sigue vigente
con H05-A y admite correcciones de enviadas/invalidadas durante captura.

Backend vuelve a comprobar identidad, CSRF, período publicado y abierto,
existencia/pertenencia del trabajo, revisión de principal y perfil actual,
colección no vacía, duplicados, malla, límites independientes 3 altas + 4 medias/bajas,
7 total y elegibilidad D03 con estado declarado. No recibe selecciones desde el
cliente para enviar: lee el borrador persistido. Error 401/403 de seguridad,
409 de estado/revisión/captura y 422 de colección/elegibilidad/clave.
El preflight CORS local permite la nueva cabecera de idempotencia.

Tras seguridad y bloqueos, la clave se consulta antes de ventana/revisión/estado:
mismo cuerpo devuelve el resultado original aun tras cierre o invalidación;
otro cuerpo da 409. Ese resultado no restaura vigencia: GET muestra estado actual.
Errores no se memorizan. Clave y cuerpo se conservan en memoria de la pantalla
para reintentar tras fallo de red; recargar descarta ese intento local y recupera
el estado del servidor.

Reutilizadas: solicitud, version_solicitud, detalle_solicitud, perfil y revisiones,
estados declarados, catálogo/malla/prerrequisitos, período y sesión.
Migraciones aditivas `0006_h05b` (vigencia, estados, eventos, idempotencia) y
`0007_h05b` (JSON de evaluación histórica). Sin reinicialización ni modificación
de filas anteriores. `version_solicitud.fundamento` guarda la evaluación completa
usada, con estados, requisitos, reglas, nombres y semestres; además conserva la FK
a la revisión académica inmutable. La consulta enviada usa esas etiquetas históricas.
Los borradores previos admiten fundamento NULL; no se les inventa un envío.
`evento_solicitud` registra envío, invalidación y renovación compatible;
`envio_idempotente` conserva huella y respuesta sin cookies ni credenciales.
D10 local: históricos y claves se conservan durante pruebas, sin borrado automático;
la política institucional de retención continúa **pendiente**, solo datos sintéticos.

Durante la aplicación inicial 0006 falló el nombre de un CHECK tras añadir la
columna (DDL MySQL no transaccional). Se corrigió con `op.f` y detección de columna
existente; se reanudó conservando datos. En concurrencia falló inicialmente la
limpieza del fixture por orden de FK; se corrigió sin excluir pruebas y se retiraron
solo sus artefactos identificados. No son fallos ocultos ni reinicializaciones.

## Firefox: prueba exacta

Con los servicios locales existentes y `.env` configurado, desde la raíz:

```bash
set -a
source .env
set +a
cd backend
.venv/bin/alembic upgrade head
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

En otra terminal: `cd frontend` y `npm start`. MySQL y Mailpit deben estar activos
(`docker compose up -d mysql mailpit` desde la raíz si hace falta).
No crear ni reabrir períodos existentes. Si no hay captura abierta, el generador
local explícito de H05-A (`.venv/bin/python -m app.db.demo_period`) crea únicamente
un período DEMOSTRACIÓN; nunca representa fechas oficiales.

1. Firefox: `http://127.0.0.1:4200/iniciar-sesion`; cuenta sintética autorizada,
   OTP de `http://127.0.0.1:8025`.
2. En Perfil académico declarar NO CURSADA para una candidata con reglas
   verificadas y sin requisitos pendientes; guardar. La ausencia de declaración
   debe seguir bloqueada, incluso si se cumplen los prerrequisitos.
3. Abrir Mi selección, elegir período con captura abierta, agregar candidata y
   prioridad. Pulsar Guardar borrador y esperar confirmación.
4. Revisar período, asignaturas, semestre curricular, prioridades y total;
   pulsar Enviar solicitud. Cancelar mantiene el borrador.
5. Pulsar otra vez Enviar solicitud y Confirmar envío. Esperar «Solicitud enviada:
   intención académica registrada. No es matrícula ni reserva de cupo».
6. Ver estado Enviada y tabla Materias enviadas. Recargar y comprobar persistencia.
   En Red de Firefox el POST submit debe responder 200; GET conserva la principal.
7. Guardar una corrección: sigue visible el envío anterior. Confirmar el nuevo
   envío: cambia vigente, conserva la misma principal y el historial en MySQL.
8. Dos pestañas con el mismo borrador: enviar en una; en la otra debe haber
   conflicto. Recargar explícitamente antes de continuar.
9. Durante captura, cambiar perfil para aprobar una candidata enviada o quitar
   su declaración: Mi selección muestra Requiere revisión y deja de tener vigente.
   Corregir, guardar y reenviar. Períodos cerrados conservan el envío previo.

La comprobación visual manual en Firefox queda **pendiente**; esta guía no afirma
que haya sido ejecutada.

## Verificación final

- `PREVIA_TEST_MYSQL=1 .venv/bin/pytest -q --tb=short`: **72 passed**, sin
  exclusiones ni skips; MySQL real. Incluye 19 casos nuevos de envío: límites,
  seguridad, D03, cambios académicos, correcciones, reintentos, rollback,
  concurrencia con conexiones reales, instantánea y conservación tras cierre.
  Un aviso preexistente de deprecación Starlette/TestClient con httpx.
- `.venv/bin/ruff check .`: aprobado. Tras la suite se corrigió únicamente el
  ajuste de línea de una cabecera constante en la prueba CORS; no cambia su valor.
- `.venv/bin/alembic check`: `No new upgrade operations detected`.
- `npm run build`: aprobado, sin advertencias.
- `node checks/submit.cjs`: 9 comprobaciones de componente aprobadas
  (carga/guardado, cuerpo sin etiquetas extra, confirmación, reintento y clave,
  confirmación de éxito y bloqueo por cambios sin guardar).
- `npx tsc src/app/features/academic/selection-rules.ts --outDir /tmp/previa-h05a --module commonjs --target es2020 --ignoreConfig`
  y `node checks/selection.cjs`: 10 comprobaciones aprobadas.
- `npx tsc src/app/demo/demand-demo.ts src/app/demo/demand-catalog.ts --outDir /tmp/previa-h01-c --module commonjs --target es2021 --ignoreConfig`
  y `node checks/demand.cjs`: aprobados. Primer intento con target es2020
  rechazó replaceAll; corregido el comando a es2021 y recompilado antes de validar.
- `git diff --check`: aprobado. Sin commits, push, servicios externos o despliegue.

Archivos: servicio drafts y modelos, integración D04 en academic, cabecera CORS
en main, migraciones 0006/0007, test_submit; componente selection, aviso y resultado
D04 en academic, cabeceras opcionales en AuthService y checks/submit.cjs; documentos
fuente actualizados con alcance H05-B y esta guía. Archivos preexistentes en
referencias/interfaz-anterior se conservan sin cambios.

**Pendientes:** recorrido visual Firefox y políticas institucionales D10/D11;
retiro/recuperación, API de historial paginado y gráficos de Demanda quedan fuera
de esta entrega. No se certifica elegibilidad universitaria.
