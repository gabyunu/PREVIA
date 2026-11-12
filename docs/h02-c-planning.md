# H02-C — Persistencia para planificación de demanda

Fecha: 2026-11-12. **Confirmado:** autorización específica para H02-C, SQLAlchemy,
Alembic y MySQL local, conservando H02-A/H02-B. No autoriza servicios, endpoints,
interfaz, selección/envío, reportes reales, administración ni cambios de autenticación.
Los textos históricos de fase 0 y de H02 pendiente no limitan esta autorización.

## Insumo y decisiones

El usuario identifica «Database Design Proposal», 27 de septiembre de 2026.
El archivo original no está disponible en el repositorio ni se ha consultado en
servicios externos. Esta entrega incorpora exclusivamente los aportes descritos
en la tarea; no atribuye otras reglas a un documento no inspeccionado.

**Incorporado:** períodos destino y ventana de captura diferenciados, capacidad
orientativa por entrada curricular/período, notas con autor/tipo/fecha y trazabilidad
de reglas. Se reutilizan usuario, roles, perfil, catálogo y versiones existentes.
No se duplican estudiantes, personal administrativo ni asignaturas.

**Descartado por contradicción con PREVIA**, si se interpreta así la propuesta:
planificación como catálogo obligatorio de oferta o disponibilidad, cupos como
reserva, horarios/paralelos, intenciones planas que sustituyan solicitudes versionadas,
registro público de administrativos, aprobación condicional de prerrequisitos,
reconfirmación y porcentajes institucionales sin padrón. No se afirma que el documento
original contenga todas esas interpretaciones; son los límites de incorporación.

Se mantienen una carrera piloto con capacidad futura multicarrera, 53 asignaturas
provisionales, prioridades alta/media/baja y máximos independientes 3 altas y 4
medias/bajas, 7 total. Prerrequisitos declarados aprobados, sin matrícula ni oferta
oficial. No se implementa ninguna nueva regla curricular.

## Tablas y restricciones implementadas

- `periodo_academico`: PK `id`; `identificador` es el código único del período
  (no se crea un segundo código redundante); `inicio_periodo` UTC nullable solo en
  borrador; `captura_desde`, `captura_hasta`, `zona_horaria`, estado administrativo
  `estado_configuracion` borrador/publicado y `revision_control > 0`.
  CHECK exige `desde < hasta` y `hasta < inicio` cuando existe inicio;
  publicado exige inicio. Abierta/cerrada será una condición calculada de ventana,
  nunca un estado administrativo independiente que habilite reaperturas.
- `planificacion_cupos`: PK `id`, FK a `malla_asignatura`, período y responsable
  usuario opcional. UNIQUE(entrada curricular, período) garantiza unicidad por
  asignatura/versión/período gracias al UNIQUE ya existente en malla_asignatura.
  `cupos_planificados` admite NULL o enteros no negativos; NULL significa
  desconocido, cero significa cero explícito. No tener fila tampoco significa cero.
  `actualizado_en` tiene valor inicial UTC; UPDATE mediante esta tabla SQLAlchemy
  genera actualización UTC. SQL directo deberá mantener esa fecha explícitamente:
  no se ha añadido un trigger ni ON UPDATE de MySQL.
- `nota_administrativa`: PK `id`, FK obligatorias a planificación y autor usuario,
  `tipo` observacion/propuesta/decision, contenido no vacío y `creado_en` UTC.
  Índice(planificación, fecha, id) para lectura cronológica. Las notas no alteran
  automáticamente los cupos ni constituyen una matrícula.

Todas las FK nuevas usan RESTRICT al borrar/actualizar. Índice de planificación
por período, UNIQUE por entrada/período e índices de FK MySQL soportan consultas.
La entrada curricular determina su versión y asignatura; no se propagan claves
redundantes que puedan divergir. No se exige planificación para expresar interés.

**Seguridad y servicios pendientes:** ninguna tabla ni FK comprueba roles. Futuras
escrituras deben verificar en backend sesión activa y rol administrador preasignado,
autor/responsable derivados por servidor, transacción y auditoría; notas deben
conservarse como historial. La FK a usuario asegura identidad, no autorización.
No se crean usuarios administrativos, asignaciones de roles ni rutas en H02-C;
el registro OTP continúa concediendo exclusivamente rol estudiante.

Se adopta aquí el orden estructural de fechas ya recomendado en el modelo.
La validación IANA/desplazamiento, reloj `ahora < inicio` al publicar, congelación
de configuración y control de revisiones quedan **pendientes de implementación**
en servicios administrativos; CHECK no implementa esos controles. DATETIME almacena
UTC por contrato, no conserva zona ni impide por sí mismo escribir hora local.
No se insertan fechas institucionales ni períodos demo permanentes.

## Metadatos de prerrequisitos

La regla pertenece a `malla_asignatura`: ya conserva `estado_regla`,
`revision_pendiente`, `prerrequisito_texto_original` y `condiciones_externas`;
las dependencias internas siguen en aristas `prerrequisito`. Esos metadatos
cubren el conjunto de requisitos de esa entrada, sin duplicarlos en cada arista.
`estado_regla` distingue propuestas y pendientes: `revision_pendiente=false`
no acredita verificación institucional. Toda la malla piloto sigue provisional.

Solo se añaden `fuente_regla` (texto/localizador de respaldo) y `regla_revisada_en`
(fecha UTC de revisión, cuando exista), ambos opcionales. No se inventa fuente ni
fecha histórica: existentes quedan NULL. La procedencia del piloto sigue documentada
en H02-A y en su archivo JSON; incorporar respaldo validado exige revisión posterior.
No se cambia el seed, el JSON, las 53 entradas, sus estados ni las 34 aristas.
No se agrega un segundo estado de verificación que sugiera aprobación oficial.

## Contrato de cálculo futuro (sin consultas ejecutables todavía)

**Confirmado para la incorporación; implementación pendiente H06/H07/H10:**

1. Base válida: principal del período en estado enviada, con puntero vigente no
   nulo; unir solo esa versión y sus detalles, con revisión académica del envío.
   Excluir borradores, retiradas, invalidadas y versiones anteriores. Respetar D04
   y conservar la instantánea tras cierre; no recalcular con el perfil actual.
2. Agrupar por período, versión de malla y entrada curricular. Demanda total =
   estudiantes distintos en esa base por asignatura/período; desglosar alta/media/baja
   con el mismo universo. No fusionar versiones por nombre o asignatura de catálogo.
3. Repetición autodeclarada = estudiante con estado reprobada de esa candidata en
   la revisión del envío. No_cursada no es repetición; desconocido impide envío.
   No expresa número de intentos ni repetición oficial.
4. Agregar demanda primero y hacer LEFT JOIN a planificación única por entrada y
   período después. No unir notas, roles, eventos, aristas ni todas las revisiones
   antes del agregado: multiplicarían filas. Si se necesitan notas, agregarlas
   separadamente. Participantes globales = DISTINCT del universo filtrado; no suma
   de subtotales por materia. Pruebas futuras deben incluir varias notas y eventos.
5. Cupos = valor registrado, incluido cero. Sin fila o con valor NULL: desconocidos.
   Brecha = demanda válida - cupos cuando estos son conocidos; en otro caso NULL,
   presentado como desconocido. No usar COALESCE(cupos, 0). Con cero, brecha = demanda;
   con cupos mayores que demanda, conservar brecha negativa, no truncarla.
6. Grupos orientativos = ceil(demanda válida / tamaño de grupo) solamente si se
   proporciona un tamaño entero positivo, identificado como parámetro de escenario;
   en ausencia de tamaño, desconocido. No se deriva tamaño de cupos, ni se crean
   paralelos oficiales ni se garantiza apertura. El tamaño institucional sigue
   **pendiente**; no hay un valor predeterminado inventado.
7. Incluir `generado_en` UTC, período, filtros, parámetro de grupos y advertencia
   de autodeclaración. Leer agregados y planificación en una instantánea consistente.
   Para reproducir planificación antigua haría falta historial adicional: esta tabla
   guarda su valor actual, no versiones históricas de capacidad. No afirmar que
   `actualizado_en` permite reconstruir capacidades anteriores.

Sin solicitudes implementadas no se crean vistas, consultas de demanda, endpoints
ni CSV conectados. La vista de demostración Angular sigue independiente. No hay
porcentajes de participación institucional ni elegibilidad oficial.

## Migración y verificación

Migración aditiva `6ce839510cac`, posterior a `26b1116c5ba7`: tres CREATE TABLE,
dos columnas nullable en malla_asignatura e índices; sin UPDATE/DELETE de datos,
sin reinicializar MySQL ni ejecutar downgrade. MySQL hace commits implícitos de DDL;
si hay fallo se debe inspeccionar el estado antes de reintentar. Downgrade elimina
las estructuras de esta entrega y requeriría autorización y respaldo; no se probó
sobre el volumen existente.

Se iniciaron los contenedores existentes con `docker compose start --wait mysql
mailpit`, conservando volumen y configuración. Antes de migrar se compararon
cantidades y SHA-256 de todas las filas de las 16 tablas existentes; después de
migrar todas conservaron contenido y cantidad. Se excluyeron del cotejo solo la
revisión técnica de Alembic y las dos columnas nuevas. Había 53 asignaturas/entradas,
34 aristas, 5 usuarios/perfiles y 5 sesiones; no se imprimieron datos personales,
digests ni secretos. La comparación se hizo antes de la suite de autenticación,
cuyas pruebas concurrentes conservan nuevas cuentas sintéticas como en H02-B.

Desde la raíz se exportaron las variables locales con `set -a`, `source .env`,
`set +a`; los comandos siguientes se ejecutaron desde `backend/` con acceso a los
servicios locales:

| Comando | Resultado |
|---|---|
| `.venv/bin/alembic upgrade head` | Exit 0, migración aplicada |
| `.venv/bin/alembic current` | `6ce839510cac (head)` |
| `.venv/bin/alembic check` | `No new upgrade operations detected` |
| `PREVIA_TEST_MYSQL=1 .venv/bin/python -m pytest -q` | 26 passed, 1 warning, 2.91 s |
| `.venv/bin/ruff check .` | All checks passed |
| `.venv/bin/ruff format --check .` | 18 files already formatted |
| `git diff --check` desde raíz | Exit 0 |

Diez casos nuevos (incluidos siete casos parametrizados de fechas/estado/revisión)
y las 16 pruebas previas. Cubren FK/RESTRICT, unicidad, períodos/mallas distintos,
NULL frente a cero, negativos, tipos y contenido de nota, fuente/fecha de regla y
actualización temporal desde SQLAlchemy. La suite anterior verifica las 53 entradas,
34 aristas, seed idempotente y rechazo de elevación de rol por autenticación.
No se afirma haber probado selección sin planificación: ese servicio no existe;
se conserva como requisito y no se introduce dependencia estructural.

Aviso: deprecación Starlette/httpx ya presente en H02-B. No se cambian dependencias
para resolverlo. No se ejecutó build frontend porque no hubo cambios de interfaz.
No se probó downgrade ni reconstrucción sobre base vacía; la evidencia corresponde
al upgrade aditivo sobre el volumen con datos existentes. Los primeros controles
Ruff detectaron formato del archivo autogenerado y un import de fixture; se
corrigieron antes de la ejecución final, que pasó.

## Archivos y pendientes

Archivos H02-C: `backend/app/db/models.py`, migración `6ce839510cac`,
`backend/tests/test_planning.py`, esta guía y notas de alcance en la documentación
fuente. Se preservaron cambios previos sin commit de H02-B; no se hicieron commits,
push, llamadas externas, instalaciones ni cambios visuales/de autenticación.

Pendientes: administración autorizada y auditada, fuentes/fechas institucionales,
validación temporal de servicio, perfil/evaluador, solicitudes versionadas y sus
transacciones, reportes/CSV reales y pruebas de deduplicación con datos de solicitudes.
Privacidad/retención y eventuales equivalencias entre mallas siguen pendientes.
