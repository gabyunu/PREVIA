# H01-D — Interfaz de acceso y creación de cuenta

## Alcance y estado

**Confirmado y autorizado para H01-D:** interfaz Angular de acceso sin contraseña,
registro exclusivo de estudiantes y vista previa OTP. Se toma la distribución de
`referencias/referencia-login.png`, sin reproducir logotipos ni fotografías.
Se conservan Inicio y todas las pantallas académicas. Sin backend, MySQL,
autenticación simulada, almacenamiento persistente, dependencias nuevas ni servicios externos.
H02 y la integración de identidad siguen sin autorización.

La documentación histórica de fase 0 se interpreta con la autorización específica
actual; esta entrega no aprueba los mecanismos técnicos pendientes de identidad.

## Archivos y componentes

- `frontend/src/app/features/auth/auth.ts`, `auth.html`, `auth.css`: componente
  contenedor Auth, cabecera institucional, pestañas, panel izquierdo y adaptación móvil.
- `frontend/src/app/features/auth/auth-form.ts`, `auth-form.html`, `auth-form.css`:
  AuthForm reutilizado para acceso y registro mediante input `registration`.
  Correo con validación de sintaxis, aviso de API ausente, vista previa OTP y mensajes
  accesibles. El código solo existe temporalmente en memoria del componente y se
  limpia al intentar verificar o cambiar de paso; no se valida ni genera un desafío.
- `frontend/src/app/features/auth/auth-presentation.ts`, `auth-presentation.html`,
  `auth-presentation.css`: presentación reutilizable y límites de PREVIA.
- `frontend/src/app/app.routes.ts`: rutas de carga diferida `/iniciar-sesion` y
  `/crear-cuenta`, antes del comodín; rutas académicas conservadas.
- `frontend/src/app/features/home/home.html`: enlaces desde Inicio.
- `docs/h01-d-access.md`: entrega, contratos y verificación.

Los estilos nuevos son locales a los componentes. No se modifican los estilos
globales, Demanda ni backend. Los cambios previos de H01-C se conservan.

## Comportamiento revisable

Solicitar código muestra que se requiere API y que no se ha enviado correo.
«Vista previa del paso OTP» permite inspeccionar el segundo paso sin simular envío.
Verificar informa que no se ha verificado ni creado sesión/cuenta; no redirige
ni concede acceso. Ambos formularios comparten el futuro flujo OTP. No hay selección
de rol, contraseñas ni creación pública de administradores.

**Pendiente:** dominios institucionales autorizados, formato/duración de OTP,
límites, sesión y decisiones técnicas de identidad. No se fijan en el formulario.
La comprobación del dominio y todos los controles de seguridad corresponderán al backend.

## Endpoints futuros

**Recomendados**, conforme a `api-design.md`, prefijo `/api/v1`; no implementados
ni invocados en H01-D:

| Método y ruta | Integración posterior |
|---|---|
| POST `/auth/otp/request` | Recibe `correo`; respuesta genérica 202 y `desafio_id`. También para reenvío; sin revelar existencia de cuenta. |
| POST `/auth/otp/verify` | Recibe `desafio_id`, `codigo`; verifica y consume OTP, crea estudiante en primer acceso o inicia sesión existente, cookie segura. Nunca acepta rol del cliente. |
| GET `/me` | Recupera identidad y permisos de la sesión validada. |
| POST `/auth/logout` | Revoca sesión con protección CSRF. |
| GET `/me/academic-profile` | Permite identificar el perfil académico por completar después del primer acceso válido. |
| PUT `/me/academic-profile` | Completa el perfil con catálogos autorizados y validación del servidor; fuera de esta interfaz. |

En la integración se deberán representar errores genéricos de verificación,
validación 422, límites 429 y servicio no disponible, sin inventar resultados.
No se necesita endpoint separado de registro público ni de promoción administrativa.

## Verificaciones ejecutadas

- `cd frontend && npm run build`: **correcto**, Angular genera `dist/previa`;
  carga diferida de auth, total inicial 343,18 kB. El entorno imprime avisos
  `Failed to create stream fd: Operation not permitted`, sin impedir la compilación.
  El primer intento desde la raíz falló por ausencia de `package.json`; se corrigió
  el directorio y se ejecutó satisfactoriamente.
- `cd frontend && ./node_modules/.bin/tsc --ignoreConfig src/app/demo/demand-demo.ts src/app/demo/demand-catalog.ts --outDir /tmp/previa-h01-c --module commonjs --target es2022 --skipLibCheck && node checks/demand.cjs`:
  **correcto**, 53 asignaturas, 80 estudiantes sintéticos, 160 intenciones;
  pasan comprobaciones existentes de demanda y CSV. Primer intento sin
  `--ignoreConfig` rechazado por TypeScript TS5112, corregido en el comando indicado.
- Comprobación estática con Node/assert: rutas académicas presentes y nuevas rutas
  anteriores al comodín; componentes de acceso sin almacenamiento web,
  contraseña ni llamadas HTTP: **correcta**.
- `git diff --check`: **correcto**.

**Limitación:** no hay Playwright/Puppeteer disponible; no se ejecutaron pruebas
reales de navegación ni revisión visual en navegador. La compilación y la revisión
estática no sustituyen esa comprobación. Pendiente revisión manual a 375 y 1280 px:
formulario visible, navegación por teclado, pestañas, ida/vuelta entre registro y
acceso, avisos OTP, y rutas académicas existentes (incluida Demanda).

## Visualizar

Desde `frontend`, ejecutar `npm start`. Abrir:

- `http://127.0.0.1:4200/` — Inicio conservado, con enlaces de acceso.
- `http://127.0.0.1:4200/iniciar-sesion` — acceso por correo.
- `http://127.0.0.1:4200/crear-cuenta` — registro de estudiante.
- `http://127.0.0.1:4200/demanda` — demostración académica existente.

Usar «Vista previa del paso OTP» para ver el segundo paso. No introducir datos reales.
