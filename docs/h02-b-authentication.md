# H02-B — Acceso local con correo y OTP

## Alcance y decisiones

**Confirmado por la tarea H02-B:** autenticación local funcional, Mailpit, sesiones
reales, alta automática exclusivamente como estudiante y conexión de las pantallas
Angular existentes. Esta autorización sustituye las notas históricas que dejaban
H02-B pendiente y permite esta parte de H05/H08; no autoriza perfil académico,
solicitudes, reportes persistidos ni administración.

**Recomendado y adoptado para esta entrega local:** parámetros siguientes,
normalización D08 (recortar espacios exteriores, dominio en minúsculas, parte local
conservada), Mailpit v1.27.10 y sesión opaca en MySQL. No son políticas
institucionales definitivas. **Pendiente:** dominios oficiales, normalización
institucional, privacidad/retención D10 y procedimiento de administración D09.
No se crean administradores ni se asigna ese rol a usuarios. Controlar un buzón
no acredita matrícula activa.

Dependencias: MySQL H02-A migrado, Docker Compose, entorno Python y dependencias
Angular existentes. No se agregaron dependencias Python/npm. El único artefacto
nuevo descargado es la imagen de Mailpit solicitada para este hito.

## Configuración local

`.env.example` describe todas las variables. Conservar el `.env` existente de
H02-A: **no sobrescribirlo** ni cambiar las credenciales del volumen inicializado.
En esta ejecución se añadió a `.env` una clave aleatoria ignorada por Git.
En otra instalación, generar una clave y añadirla manualmente al archivo local:

```bash
python3 -c 'import secrets; print(secrets.token_hex(32))'
```

| Variable | Valor local predeterminado / requisito |
|---|---|
| AUTH_HMAC_KEY | Obligatoria, mínimo 32 caracteres; usar la clave aleatoria generada |
| AUTH_ALLOWED_DOMAINS | estudiantes.example.test; lista exacta separada por comas |
| SMTP_HOST / SMTP_PORT | 127.0.0.1 / 1025 (Mailpit) |
| AUTH_FRONTEND_ORIGIN | http://127.0.0.1:4200 |
| AUTH_COOKIE_SECURE | false exclusivamente para HTTP local; true bajo HTTPS |
| AUTH_OTP_SECONDS / AUTH_OTP_ATTEMPTS | 600 / 5 |
| AUTH_RESEND_SECONDS | 60 |
| AUTH_EMAIL_HOURLY / AUTH_IP_HOURLY | 5 / 30 emisiones por ventana de una hora |
| AUTH_SESSION_SECONDS / AUTH_IDLE_SECONDS | 28800 / 1800 |

Los dominios de esta entrega deben terminar en `.test` o `.invalid`; se rechazan
configuraciones de dominios reales. SMTP solo admite `127.0.0.1`, `localhost` o
`mailpit`; no hay credenciales, relay ni proveedor externo configurados. Los
puertos publicados de Mailpit (SMTP 1025, web 8025) están ligados a loopback.
Usar **127.0.0.1 consistentemente**, sin mezclarlo con localhost: las cookies,
SameSite y el origen permitido dependen del host. El cliente Angular utiliza la API
local en http://127.0.0.1:8000/api/v1; esta entrega no tiene configuración productiva.
Cambiar AUTH_HMAC_KEY invalida sesiones/desafíos y reinicia las claves de límites;
no rotarla para evadir límites de pruebas.

## Arranque y prueba exacta en Firefox

Desde la raíz del repositorio:

```bash
docker compose up -d --wait
docker compose ps
set -a
source .env
set +a
cd backend
.venv/bin/alembic upgrade head
.venv/bin/alembic current
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-proxy-headers
```

Se presupone el entorno existente de H02-A. No se ejecuta seed ni se reinicializa
MySQL. `--no-proxy-headers` impide que cabeceras de proxy elegidas por el cliente
modifiquen la IP usada para límites; aquí no hay proxy autorizado.
En una segunda terminal desde la raíz:

```bash
cd frontend
npm start
```

1. Abrir Firefox en http://127.0.0.1:4200/iniciar-sesion.
2. Introducir `estudiante@estudiantes.example.test` y pulsar **Solicitar código**.
   También se puede comenzar en `/crear-cuenta`: ambas pantallas usan el mismo
   flujo; el backend determina si corresponde crear la cuenta.
3. En otra pestaña abrir http://127.0.0.1:8025. Mailpit es el buzón local de prueba,
   sin entrega al correo real. Abrir el mensaje PREVIA dirigido a esa cuenta.
4. Copiar los ocho dígitos y verificarlos en la pestaña PREVIA antes de diez minutos.
   Se vuelve a Inicio, aparece el correo autenticado y el botón **Cerrar sesión**.
5. Recargar Inicio: `/api/v1/me` recupera la identidad desde la cookie de sesión.
   Las áreas académicas siguen siendo demostraciones sintéticas en memoria.
6. Pulsar **Cerrar sesión**: la sesión se revoca en MySQL y se borran las cookies.
   Volver a acceder con ese correo reutiliza la misma cuenta, sin crear otra.
7. Para probar errores, introducir ocho dígitos incorrectos; cinco intentos agotan
   el desafío. Para reenviar, esperar al menos 60 segundos; el código anterior
   deja de ser válido. Vencimiento, consumo e inexistencia tienen el mismo mensaje
   para evitar filtraciones. Un límite muestra el tiempo de espera.

En herramientas de desarrollo de Firefox, Red permite ver `/me` (200 con sesión,
401 sin ella), request (202), verify (200 o 401) y logout (204). La cookie
`previa_session` es HttpOnly, SameSite=Strict y tiene ruta `/api/v1`; no hay token
de sesión accesible a JavaScript ni persistencia en localStorage. `previa_csrf`
puede leerla el cliente para enviar `X-CSRF-Token`, incluso tras una recarga.
No pegar códigos, cookies ni claves en capturas o registros compartidos.

## Contratos y controles implementados

- `POST /api/v1/auth/otp/request`: `{correo}` → 202 con `mensaje`, `desafio_id`
  opaco y `vigencia_segundos`. Mismo cuerpo para cuentas nuevas, existentes y
  dominios no admitidos; estos últimos no generan mensajes ni desafíos utilizables.
- `POST /api/v1/auth/otp/verify`: `{desafio_id, codigo}` → 200 con `usuario`
  `{id, correo, roles}`, `csrf_token` y cookies. Error genérico 401 para OTP
  incorrecto, vencido, agotado, invalidado, consumido o cuenta suspendida.
- `GET /api/v1/me`: 200 con identidad propia, `Cache-Control: no-store`; exige
  sesión vigente y cuenta activa. Actualiza actividad. Sin sesión: 401.
- `POST /api/v1/auth/logout`: origen exacto y cabecera `X-CSRF-Token` válida →
  204, revocación y eliminación de cookies; sin sesión 401, CSRF/origen inválido 403.

Pydantic rechaza campos adicionales y formato incorrecto (422 genérico sin devolver
el cuerpo recibido). No se acepta rol desde el cliente. Emisión limitada responde
429 con Retry-After, accesible por CORS; SMTP no disponible responde 503 sin
registrar el código. CORS permite solo el origen local configurado y credenciales.
Todas las operaciones POST, también las previas a la sesión, exigen origen exacto;
logout exige además token CSRF ligado a la sesión mediante digest. Fetch Metadata
rechaza escrituras cross-site. La cookie SameSite=Strict añade protección.

OTP de ocho dígitos generado con `secrets.randbelow`, desafío y sesión con
`secrets.token_urlsafe(32)`. HMAC-SHA256 con clave fuera de MySQL protege OTP,
sesión y CSRF; comparación de OTP/CSRF en tiempo constante. El OTP claro solo
vive transitoriamente al emitir y en el correo de Mailpit. Sesión absoluta e
inactividad se comprueban en backend; suspensión impide acceso. Una autenticación
nueva revoca la sesión presentada y genera otra. No se registran códigos, tokens,
claves ni cuerpos de autenticación en logs.

Además de los límites de emisión configurables, verificación admite como máximo
50 peticiones/hora por IP y 25/hora por correo, compartidas entre desafíos.
La IP procede de la conexión, no se leen X-Forwarded-For en la aplicación.
Los límites usan claves HMAC, sin guardar direcciones IP en claro.

## Persistencia, transacciones y límites

La migración `26b1116c5ba7`, posterior a `0001`, **solo crea** `rol`,
`usuario_rol`, `desafio_otp`, `sesion`, `evento_seguridad`, `limite_auth` y
`auth_control`. Inserta los nombres de roles y un mutex; no asigna administradores,
no altera tablas académicas ni carga o elimina sus datos. La sesión añade
`csrf_digest` y `ultimo_en` al diseño conceptual para CSRF e inactividad.

Un mutex transaccional MySQL (`SELECT ... FOR UPDATE` sobre `auth_control`)
serializa operaciones de identidad entre procesos. Emisión/reenvío, límites,
consumo, alta de usuario/perfil sin revisión curricular, asignación exclusivamente
estudiante y sesión quedan protegidos. UNIQUE de correo y perfil refuerza la
unicidad. El consumo/alta/sesión se confirman juntos; una excepción revierte todo.
Es una solución simple para el volumen local: serializa también SMTP, con timeout
de cinco segundos, y no se presenta como arquitectura de alta concurrencia.
Un fallo posterior al envío puede dejar un correo no utilizable; solicitar otro
tras la espera resuelve ese caso sin atajos de autenticación.

Eventos contienen solo tipo, instante UTC y actor cuando existe; no correos, IP,
OTP ni tokens. Se conservan datos sintéticos durante las pruebas, sin limpieza
automática; retención institucional sigue pendiente D10. Mailpit no tiene volumen
nuevo: su buzón de prueba puede perderse al recrear el contenedor. La sesión no
concede privilegios administrativos; no hay endpoints administrativos en este hito.
La vista visual Demanda sigue usando datos sintéticos públicos de demostración.

## Verificación ejecutada

Desde la raíz con variables `.env` exportadas; comandos Python desde `backend/`:

| Comando | Resultado |
|---|---|
| `docker compose up -d --wait mailpit` | Mailpit iniciado y saludable |
| `docker compose ps` | MySQL 8.4.8 y Mailpit v1.27.10 saludables |
| `.venv/bin/alembic upgrade head` | Migración aditiva aplicada |
| `.venv/bin/alembic current` | 26b1116c5ba7 (head) |
| `.venv/bin/alembic check` | No new upgrade operations detected |
| `PREVIA_TEST_MYSQL=1 .venv/bin/python -m pytest -q` | 16 passed; aviso de deprecación Starlette/httpx |
| `.venv/bin/ruff check .` | All checks passed |
| `.venv/bin/ruff format --check .` | 16 archivos con formato correcto |
| `.venv/bin/python -m pip check` | No broken requirements found |
| `npm run build` desde frontend | Compilación Angular correcta |

Incluye las cinco pruebas existentes (salud y persistencia) y once nuevas de
identidad: SMTP real a Mailpit y verificación desde el mensaje; cuenta nueva y
existente; unicidad; incorrecto, vencido, reenvío, agotado y reutilizado; cookies,
inactividad y caducidad absoluta; suspensión; logout/revocación; origen/CSRF/CORS;
límites por correo/IP; rechazo de elevación de rol; fallo SMTP y rollback al fallar
la creación de sesión. La prueba concurrente usa conexiones MySQL independientes:
dos emisiones → 202/429, dos consumos → 200/401 y una sola cuenta.
Las pruebas de catálogo comprobaron nuevamente las 53 entradas y 34 aristas.
No se sustituyó MySQL por SQLite.

Las pruebas habituales hacen rollback; la de concurrencia conserva únicamente
cuentas `race-…@estudiantes.example.test`, sesiones y eventos sintéticos para
comprobar commits y bloqueos reales. Mailpit conserva correos sintéticos `smtp-…`.
No se borraron volúmenes, ni se reinició MySQL, ni se hicieron commits/push.

La primera ejecución detectó un problema de precisión temporal DATETIME: una
fracción de segundo redondeada disparaba límites antes de tiempo; se corrigió con
instantes UTC a segundos y separación entre cooldown y máximo horario. La suite
completa posterior pasó. Angular emitió mensajes del entorno `Failed to create
stream fd: Operation not permitted`, pero el comando terminó con código 0 y
produjo los bundles. No se actualizan dependencias por el aviso de deprecación.
La prueba visual/manual en Firefox queda pendiente; no se presenta como ejecutada.

## Archivos de la entrega

- `compose.yaml`, `.env.example`: Mailpit y configuración de identidad local.
- `backend/app/auth.py`, `backend/app/main.py`: contratos, SMTP, seguridad y CORS.
- `backend/app/db/models.py` y migración `26b1116c5ba7`: tablas aditivas.
- `backend/tests/test_auth.py`: pruebas API, MySQL, Mailpit y concurrencia.
- `frontend/src/app/features/auth/`: servicio y conexión de formularios existentes;
  textos actualizados sin rediseño de estilos.
- `frontend/src/app/demo/demo.ts` y `demo.html`: identidad real y cierre de sesión;
  datos y comportamiento académico continúan en demostración.
- Documentación fuente y esta guía: autorización, alcance y evidencia H02-B.

Pendientes excluidos: perfil académico, prerrequisitos, envío de solicitudes,
reportes conectados a MySQL, administración, SMTP institucional y despliegue.
