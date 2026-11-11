# H02-A — MySQL y persistencia académica inicial

## Alcance y decisiones

**Confirmado por la autorización de H02-A:** MySQL local, SQLAlchemy, Alembic,
nueve tablas académicas y carga reproducible de la propuesta del piloto. Esta
entrega incorpora la base de catálogo/perfiles prevista en H03/H04 sin implementar
sus servicios ni endpoints. La restricción documental de fase 0 y el alcance
frontend de las notas anteriores no aplican a esta autorización específica.
Angular y Demanda permanecen sin cambios. Sin cuentas precargadas ni datos personales.

**Recomendado/adoptado para desarrollo local:** MySQL 8.4.8, InnoDB, utf8mb4 con
comparación sensible a mayúsculas y acentos, PyMySQL síncrono, puerto 3307 enlazado
a localhost, volumen `previa_mysql_data`. No hay creación automática de tablas en
FastAPI. `/health` conserva su significado de disponibilidad del proceso API.

**Pendiente:** nombre oficial de carrera, códigos institucionales, versión oficial,
validación curricular, política de normalización del correo (D08), privacidad y
retención (D10), cambios de carrera/malla y correcciones históricas (D11).
La colación sensible evita decidir implícitamente la normalización de correo;
la capa de identidad deberá normalizarlo antes de insertar. No hay autenticación.

## Tablas y relaciones

La migración `0001` crea:

- `carrera`: identidad con código local único.
- `version_malla`: pertenece a carrera; versión única por carrera y revisión positiva.
- `asignatura`: identidad estable de catálogo local única.
- `malla_asignatura`: une versión y asignatura, con semestre positivo y etiquetas
  curriculares; única por versión/asignatura.
- `prerrequisito`: aristas directas AND; ambas FK compuestas deben referenciar
  asignaturas de la misma versión; PK triple y CHECK sin autorreferencia.
- `usuario`: correo normalizado único, fecha UTC y estado activo; sin contraseñas.
- `perfil_estudiante`: identidad estable única por usuario.
- `revision_perfil`: instantánea numerada por estudiante, malla y semestre declarado;
  conserva claves para futuras versiones de solicitudes.
- `estado_academico_declarado`: PK revisión/entrada curricular; FK compuestas
  garantizan coincidencia de malla con revisión y entrada; solo aprobada, reprobada
  y no_cursada. Omitir una fila significa desconocido.

Alembic añade su tabla técnica `alembic_version`. Las FK usan RESTRICT, sin cascadas
que eliminen historial. Las revisiones deben tratarse como instantáneas completas
inmutables por los servicios futuros: el esquema por sí solo no impide UPDATE.
La publicación inmutable, permisos y serialización de revisiones requieren esos
servicios; no se exponen escrituras API en H02-A. CHECK no detecta ciclos; el
importador recorre el grafo antes de cargar.

Se conserva el diseño previsto para períodos, solicitudes, versiones y eventos,
pero esas tablas y sus reglas transaccionales no forman parte de esta entrega.

## Carga de la propuesta

`python -m app.db.seed` lee directamente
`referencias/malla-piloto/PREVIA_malla_piloto_propuesta.json`; no duplica el catálogo
en otro fixture. Comprueba 53 identidades únicas, referencias internas y ausencia
de ciclos. En una transacción crea una carrera con etiqueta explícita de demostración,
una malla **borrador**, 53 asignaturas/entradas y 34 aristas. No crea usuarios.

`DEMO-PILOTO-NO-OFICIAL` y `demo-piloto:Pxx-yy` son identificadores internos,
nunca códigos institucionales. El identificador de versión incluye una huella de
la fuente. Una segunda carga compara contenido y reutiliza las mismas identidades;
si la fuente cambia o el contenido persistido diverge, rechaza sin sobrescribirlo.
No es un importador concurrente ni publica o migra versiones automáticamente.

Cada entrada conserva `estado_regla`, `revision_pendiente`, texto original y
`condiciones_externas`. Las aristas internas se almacenan en `prerrequisito`, no
como JSON. El JSON solo conserva condiciones externas que aún no son asignaturas
del catálogo; no inventa una asignatura Inglés II.

Hay **18 entradas pendientes**: cinco «Ninguno identificado», nueve itinerarios,
Inglés III por Inglés II* externo, y Proyecto de Titulación I, Redacción de Proyecto
de Investigación e Integración Profesional y Social. Cuatro entradas tienen
«Ninguno» explícito propuesto. Las otras 31 tienen requisitos internos propuestos.
Toda la fuente sigue sin validación institucional; `revision_pendiente=false`
no significa regla oficial. Ninguna lista vacía implica automáticamente ausencia
confirmada: un evaluador futuro debe considerar los metadatos, bloquear condiciones
pendientes y distinguir los tres estados declarados de la ausencia de declaración.
No hay evaluador de elegibilidad implementado en esta entrega.

## Instalación y operación

Desde la raíz, con Docker/Compose disponibles y Python 3.14:

```bash
cp .env.example .env   # solo la primera vez; no sobrescribir configuración existente
# Editar .env local si corresponde. Sus valores iniciales son ficticios.
docker compose up -d --wait
docker compose ps
cd backend
python3.14 -m venv .venv  # solo si todavía no existe
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m pip install --no-deps -e .
set -a
source ../.env
set +a
.venv/bin/alembic upgrade head
.venv/bin/alembic current
.venv/bin/python -m app.db.seed
.venv/bin/python -m app.db.seed
.venv/bin/alembic check
PREVIA_TEST_MYSQL=1 .venv/bin/python -m pytest -q
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/python -m pip check
```

`source` presupone que el archivo local es de confianza y usa sintaxis de shell.
Compose lee `.env`, pero Alembic y el seed reciben variables del entorno; no cargan
archivos implícitamente. URL construida con `URL.create`, sin interpolar contraseñas.
La instalación editable puede descargar Setuptools >=77 en un entorno de
construcción aislado; requiere acceso autorizado al índice de paquetes. Las dependencias de ejecución/desarrollo quedan fijadas
en `requirements.lock`; la instalación de H02-A se realizó en el venv existente.

Las cuatro pruebas MySQL se omiten sin `PREVIA_TEST_MYSQL=1`; la prueba existente
`/health` no requiere BD. Las pruebas de integración usan rollback para sus cambios
sintéticos y requieren una BD local dedicada con el piloto, no una BD con datos reales.

Desde la raíz:

```bash
docker compose stop mysql       # detener; conserva el volumen
# Volver a iniciar:
docker compose up -d --wait
# Reinicio y comprobación de salud:
docker compose restart mysql
docker compose up -d --wait
```

`docker compose down` elimina contenedor/red y conserva el volumen. No usar
`down -v` si se desea conservar los datos. Cambiar contraseñas de `.env` no actualiza
las credenciales de un volumen ya inicializado. No se modifica configuración Docker,
pertenencia a grupos ni permisos globales; un fallo de acceso requiere autorización
del operador. MySQL hace commits implícitos de DDL: una migración fallida puede dejar
tablas parciales y debe inspeccionarse antes de reintentar; no borrar datos a ciegas.

## Verificación de esta entrega

Con CPython 3.14.4 se instalaron y ejecutaron SQLAlchemy 2.0.57, Alembic 1.20.1,
PyMySQL 1.2.4 y sus dependencias. Compatibilidad comprobada en esta plataforma,
no garantía para otras plataformas.

- `docker compose up -d --wait`: MySQL 8.4.8 saludable.
- `alembic upgrade head`: revisión 0001 aplicada; `alembic check`: sin diferencias.
- Dos ejecuciones del seed: ambas 53 asignaturas, 34 aristas y 18 pendientes.
- `PREVIA_TEST_MYSQL=1 .venv/bin/python -m pytest -q`: 5 pruebas pasaron,
  incluida `/health`, unicidades, FK, CHECK, mallas ajenas, idempotencia y rechazo
  de contenido divergente. No se utiliza SQLite como evidencia de integridad.
- `ruff check .`, `ruff format --check .` y `pip check`: correctos.
- Tras `docker compose restart mysql` y espera de salud: revisión 0001, 53
  asignaturas/entradas y 34 aristas persistidas, cero usuarios. Las cinco pruebas
  volvieron a pasar y Alembic siguió sin detectar diferencias.
- `git diff --check`: correcto; `.env` confirmado como ignorado por Git.

Una ejecución de pytest dentro del sandbox quedó bloqueada y fue interrumpida;
no se cuenta como prueba aprobada. Los resultados anteriores corresponden a las
ejecuciones completas con acceso autorizado.

La primera migración detectó un nombre UNIQUE duplicado; se corrigió y, con permiso
explícito, se retiraron las siete tablas vacías parciales antes de repetirla.
El sandbox bloqueó inicialmente el socket Docker y la conexión TCP; los comandos
se ejecutaron después con autorización, sin cambios globales.

## Archivos y continuación

Cambios: `compose.yaml`, `.env.example`, dependencias backend, `app/db/`,
`alembic.ini`, `alembic/`, `tests/test_persistence.py`, esta guía y referencias
cruzadas en documentación. `.env` local ignorado, con valores ficticios.

H02-B queda **pendiente de autorización y definición de alcance**. No se presume
que incluya autenticación. OTP, sesiones, roles, correo local, límites de intentos,
CSRF y dominios autorizados siguen pendientes; no existen cuentas reales ni
endpoints nuevos. Solicitudes y su historial transaccional corresponden a entregas
posteriores. No se hicieron commits, push ni despliegues.
