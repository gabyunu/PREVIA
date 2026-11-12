# H06 — Demanda de solicitudes persistidas del piloto

**Confirmado por esta tarea:** consulta administrativa y CSV desde MySQL; se
mantienen OTP, D03, D04 y el diseño previo. H06 sustituye las restricciones
históricas que dejaban pendientes los reportes reales en H05. Solo entorno local,
cuentas sintéticas y datos públicos autorizados; «persistido» describe solicitudes
registradas por el flujo del piloto, no certificación ni datos universitarios reales.

**Recomendado y adoptado localmente:** acceso con rol `administrador` asignado
mediante comando explícito de operador con acceso a la base local. No hay endpoint
de promoción, privilegios por dominio ni cuentas privilegiadas predeterminadas.
**Pendiente:** políticas institucionales de privacidad/retención, divulgación de
agregados pequeños, alta administrativa institucional y fuentes oficiales. No se
resuelven silenciosamente ni se habilita despliegue.

## Consulta y conteos

- `GET /api/v1/admin/demand/options`: períodos y versiones de malla existentes.
- `GET /api/v1/admin/demand`: JSON agregado, sin correos, nombres ni IDs de estudiantes.
- Misma ruta con `formato=csv`: CSV UTF-8 con BOM, fecha UTC, filtros, indicadores,
  aviso y filas agregadas; textos neutralizados frente a fórmulas de hoja de cálculo.
- Filtros: `periodo_id`, `malla_id`, `q` (nombre/código/ID curricular), `semestre`
  curricular, `prioridad=alta|media|baja`; `orden=descending|ascending|name|semester`;
  `tamano_grupo` opcional (entero 1–1000000). Parámetros inválidos: 422.
- Todas las rutas exigen sesión activa y rol administrativo actual: 401 sin sesión,
  caducada/revocada/suspendida; 403 estudiante. Respuestas sin caché.

Una consulta de hechos une únicamente `solicitud.estado = enviada` con su
`version_vigente_id`, versión y detalles. No se toma MAX(numero), trabajo ni eventos.
La consulta se agrega en backend dentro de la transacción; nunca se envían los
hechos individuales a Angular. Las restricciones UNIQUE existentes impiden doble
principal estudiante/período y doble detalle por versión/asignatura. Los
participantes usan un conjunto de estudiantes del universo filtrado, incluso al
consultar varios períodos; no se suman subtotales de personas.

Una corrección guardada mantiene el envío anterior; al enviar se cuenta solamente
la sustituta. D04 ya invalida toda la principal durante captura y conserva el
histórico cerrado; H06 sigue ese estado sin recalcular reglas con el perfil actual.
Nombre y semestre de asignatura proceden del fundamento de H05-B, con respaldo de
la entrada curricular para versiones sin esa etiqueta. La repetición usa el estado
histórico reprobada, nunca el perfil actual ni intentos inferidos.

Cada fila tiene período, ID de versión de malla y entrada curricular propios.
Incluso con asignatura de catálogo compartida, dos mallas producen filas separadas.
El indicador de asignaturas cuenta entradas curriculares distintas del universo
filtrado; una misma entrada en varios períodos cuenta una vez en ese indicador,
aunque conserve filas por período. Intenciones y las tres prioridades son conteos
separados. El resumen por semestre cuenta personas distintas en cada semestre;
no deben sumarse esos subtotales. No se calcula participación institucional.

Cupos se unen por período y entrada curricular. Ausencia de planificación o NULL
se muestra como «Desconocido»; 0 se conserva. Grupos = techo(total/tamaño de
referencia); sin tamaño no se calculan. Ni cupos ni grupos validan selección ni
representan oferta oficial. CSV y pantalla usan los mismos filtros y servicio;
cada exportación consulta una instantánea nueva, por lo que una modificación
concurrente puede hacer que difiera de una pantalla cargada anteriormente.

## Configuración administrativa controlada

No se ejecuta automáticamente ni se concede acceso a ninguna cuenta en esta entrega.
El operador debe elegir una cuenta de prueba separada, del dominio ficticio ya
permitido, iniciar sesión una vez por OTP y **no guardar perfil académico**.
Obtener su ID en la respuesta propia `GET /api/v1/me` desde Red en Firefox.
No introducir correos ni secretos en archivos versionados.

Con `.env` local configurado, desde la raíz:

```bash
set -a
source .env
set +a
cd backend
# Sustituir 123 por el ID verificado de esa cuenta y la referencia del operador.
.venv/bin/python -m app.db.admin_access --user-id 123 --operator operador-local --confirm-local-test
```

El comando exige cuenta existente y activa; rechaza cualquier cuenta con revisión
académica. En una transacción bloqueada asigna únicamente el rol administrativo,
retira el rol estudiante, registra `admin_local_concedido` con cuenta destinataria,
instante y referencia del operador y revoca sus sesiones previas. El actor SQL es
el operador local; `actor_usuario_id` del evento identifica la cuenta destinataria,
no afirma que esa cuenta se haya promovido a sí misma. La referencia identifica al
operador bajo responsabilidad local, sin certificación externa. Se requiere OTP
nuevo para continuar. El acceso al comando y credenciales MySQL queda en manos del
operador del entorno. No modifica los mecanismos OTP ni crea contraseñas.

## Demostración en Firefox

Servicios locales existentes: MySQL y Mailpit; API en `127.0.0.1:8000` con
`.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000` desde backend y entorno
cargado; Angular con `npm start` desde frontend. No reinicializar MySQL. H06 no
requiere migración nueva; usar las migraciones H05 existentes. Si no existe período
abierto, el generador explícito de H05-A crea un período etiquetado DEMOSTRACIÓN:
`.venv/bin/python -m app.db.demo_period`; no reabre ni cambia períodos anteriores.

1. Abrir `http://127.0.0.1:4200/iniciar-sesion` en Firefox. Usar la cuenta sintética
   de estudiante y OTP de Mailpit (`http://127.0.0.1:8025`). En Perfil académico,
   declarar NO CURSADA una candidata con reglas verificadas y prerrequisitos
   declarados aprobados; guardar. La ausencia de declaración sigue bloqueada.
2. En Mi selección elegir captura abierta, agregar asignatura y prioridad; guardar
   borrador. Conservar período, versión curricular y asignatura para comparar.
3. Pulsar Enviar solicitud y Confirmar envío. Esperar «Solicitud enviada»;
   recargar y comprobar persistencia. En Red: POST submit 200 y GET con estado
   enviada y `version_vigente_id`. Con sesión estudiantil Demanda debe mostrar
   denegación administrativa; no debe mostrar los agregados persistidos.
4. Configurar la cuenta administrativa separada con el procedimiento anterior.
   Cerrar sesión de estudiante; iniciar sesión administrativa con OTP nuevo.
   Alternativamente usar una ventana privada para mantener sesiones separadas.
5. Abrir `/demanda`, fuente «Solicitudes persistidas del piloto». Filtrar el mismo
   período y versión de malla. Ver la asignatura y prioridad enviadas; actualizar
   si la pantalla estaba abierta. Cada intención añade uno a su fila; participantes
   aumenta solo si esa persona aún no participaba en el universo consultado.
6. Exportar CSV: comprobar período, malla, prioridades y ausencia de datos personales.
   Si hay planificación, comprobar cero explícito y desconocido por separado.
7. Como estudiante guardar corrección de prioridad: el reporte sigue mostrando
   el envío anterior. Enviar corrección y actualizar Demanda: cambia prioridad,
   sin duplicar personas ni intención. Durante captura aprobar la enviada o
   retirar su declaración del perfil invalida toda la principal y la excluye.
8. Cambiar fuente a «Demostración sintética H01-C»: aparecen exclusivamente el
   fixture y su CSV sintético. Volver a persistidas recupera el reporte independiente.

Recorrido visual manual en Firefox **pendiente**; estos pasos son guía reproducible,
no afirmación de ejecución visual.

## Archivos y verificación

Nuevos: `backend/app/demand.py`, `backend/app/db/admin_access.py`,
`backend/tests/test_demand.py`, `frontend/checks/demand-real.cjs`, copia independiente
`frontend/src/app/demo/demand-synthetic.ts/html` y esta guía. Modificados por H06:
registro del router en `backend/app/main.py`, `frontend/src/app/demo/demand.ts/html`
y notas de alcance en documentos fuente. Sin cambios nuevos a modelos, migraciones,
autenticación, reglas académicas, CSS ni datos MySQL de la aplicación.

Los cambios H05-B y referencias ya presentes en el árbol de trabajo se conservan.
No se realizaron commits, push, despliegues ni llamadas a servicios externos.

Verificación ejecutada:

- `PREVIA_TEST_MYSQL=1 .venv/bin/pytest -q --tb=short`: **79 passed**, sin skips,
  sobre MySQL real; aviso preexistente Starlette/TestClient–httpx. Incluye H05 y
  siete casos H06: borrador/envío/corrección, prioridades, únicos, cupos ausentes,
  NULL/0, invalidación y cierre, separación real entre dos mallas compartiendo
  asignatura de catálogo, dos estudiantes, permisos, revocación/suspensión y CSV.
- `.venv/bin/ruff check .`: aprobado en backend.
- `.venv/bin/alembic check`: `No new upgrade operations detected`.
- `npm run build`: aprobado sin advertencias.
- `node checks/demand-real.cjs`: fuente persistida por defecto, filtros, CSV,
  denegación, limpieza tras error y respuestas fuera de orden aprobados.
- `node checks/submit.cjs`: nueve comprobaciones H05-B aprobadas.
- `./node_modules/.bin/tsc src/app/features/academic/selection-rules.ts --outDir /tmp/previa-h05a --module commonjs --target es2020 --ignoreConfig`
  y `node checks/selection.cjs`: diez comprobaciones H05-A aprobadas.
- `./node_modules/.bin/tsc src/app/demo/demand-demo.ts src/app/demo/demand-catalog.ts --outDir /tmp/previa-h01-c --module commonjs --target es2021 --ignoreConfig`
  y `node checks/demand.cjs`: regresión H01-C aprobada.
- Prettier aplicado a los componentes de Demanda y su comprobador nuevo;
  `git diff --check`: aprobado.

El primer intento de MySQL/Alembic dentro del sandbox falló por bloqueo de sockets
locales; las ejecuciones completas anteriores se realizaron con acceso local
habilitado. Un primer comando del comprobador H06 se lanzó desde la raíz y no
halló `checks/`; se corrigió el directorio a frontend y pasó. Los errores iniciales
de longitud de líneas de Ruff se corrigieron antes de la verificación final.
