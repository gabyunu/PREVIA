# H04-A — Perfil académico autodeclarado

## Alcance y decisiones

**Confirmado:** H04-A permite a la cuenta estudiante autenticada consultar y guardar
su perfil propio y las declaraciones de las 53 asignaturas existentes, agrupadas
en diez semestres curriculares. La pantalla conserva cabecera azul, pestañas,
menú lateral, tipografía, colores y tablas existentes.

**Recomendado y adoptado para este piloto local:** usar las tablas actuales sin
migraciones; revisiones completas e inmutables numeradas por estudiante, última
revisión como estado actual y bloqueo transaccional con revisión esperada.
Se conserva el bloqueo de identidad existente antes de bloquear el perfil.
Esto serializa operaciones en el piloto; no se presenta como solución de escala.

El contrato preliminar contemplaba catálogos publicados, pero H02-A dejó la única
malla piloto en borrador. La autorización explícita H04-A permite consultar y
elegir ese borrador exclusivamente bajo el código de carrera existente
DEMO-PILOTO-NO-OFICIAL, sin publicar ni cambiar el catálogo. Si no existe exactamente
una versión piloto, la API informa conflicto; no elige otra silenciosamente.

**Pendiente:** cambios de carrera/malla bajo D11, fuentes institucionales oficiales,
privacidad/retención institucional y elegibilidad. No se implementan solicitudes,
revalidación D04, reportes persistidos, administración ni integración institucional.
No hay tablas de solicitudes en esta entrega: solicitudes_afectadas es una lista
vacía; cuando existan, su actualización transaccional será necesaria antes de
habilitar ese flujo. Los prerrequisitos se leen como referencia propuesta y no se
alteran ni se usan para impedir la declaración de resultados.

No se crean carreras ni asignaturas operativas. Un caso de prueba crea referencias
sintéticas de otra malla dentro de una transacción que siempre se revierte.

## Endpoints implementados

Todos usan prefijo /api/v1, sesión vigente, cuenta activa e identidad de estudiante.
Respuestas con Cache-Control: no-store.

| Método y ruta | Resultado |
|---|---|
| GET /careers | Única carrera piloto existente |
| GET /curricula?career_id=… | Única versión piloto para la carrera consultada |
| GET /curricula/{id} | Versión, advertencia provisional, 53 asignaturas ordenadas por semestre e ID y aristas propuestas |
| GET /me/academic-profile | revision, malla_id, semestre_declarado, estados explícitos, advertencia |
| PUT /me/academic-profile | Nueva revisión completa, mensaje de éxito y solicitudes_afectadas vacía |

Sin revisión guardada: revision=0, malla_id=null, semestre_declarado=null, estados=[].
PUT requiere revision_esperada, malla_id, semestre_declarado entero positivo y
estados [{malla_asignatura_id, estado}]. Los valores de API/BD son aprobada,
reprobada y no_cursada; Angular presenta APROBADA, REPROBADA y NO CURSADA.
Una entrada omitida vuelve a desconocida; no existe estado persistido desconocido.
El semestre declarado es analítico, sin inferencia de aprobaciones ni límite
institucional inventado.

PUT exige origen permitido y X-CSRF-Token de la sesión. No admite usuario_id,
estudiante_id ni campos adicionales. El dueño se obtiene exclusivamente de la
sesión, con relación usuario → perfil_estudiante. Pydantic valida tipos y estados;
el servicio valida revisión, duplicados y pertenencia a la malla antes de insertar.
La clave primaria compuesta y las FK existentes refuerzan unicidad y pertenencia.

Errores: 401 sesión inválida; 403 cuenta sin perfil/origen/CSRF; 404 malla
inexistente o ajena al piloto; 409 revision_obsoleta, cambio_malla_no_habilitado
o piloto ambiguo/no disponible; 422 estructura, estado, duplicados o fuera_de_malla.
La revisión obsoleta requiere recargar explícitamente y volver a editar; no se
reintenta sobre una revisión distinta ni se sobrescriben cambios silenciosamente.

## Persistencia y archivos

Lecturas: carrera, version_malla, malla_asignatura, prerrequisito.
Escrituras académicas: revision_perfil y estado_academico_declarado.
Identidad/seguridad reutilizadas: usuario, perfil_estudiante, sesion y auth_control.
Cada revisión y sus estados se insertan en una sola transacción; un fallo revierte
ambos. Las revisiones anteriores no se actualizan ni se eliminan.
No se ejecutaron migraciones, seed, reinicializaciones ni borrados de MySQL.

- backend/app/academic.py: catálogo piloto, modelos de entrada, consulta y guardado.
- backend/app/main.py: registro de rutas y CORS para PUT.
- backend/tests/test_academic.py: seis pruebas de integración sobre MySQL.
- frontend/src/app/features/academic/academic.ts y academic.html: pantalla conectada.
- frontend/src/app/features/auth/auth-service.ts: llamadas PUT con credenciales y CSRF.
- frontend/src/app/app.routes.ts y demo/demo.ts, demo/demo.html: acceso en pestañas y menú.
- docs/requirements.md, decisions.md, architecture.md, roadmap.md y api-design.md:
  nota de autorización y alcance H04-A que contextualiza restricciones históricas.

La pantalla carga desde la API al entrar o recargar y elimina sus datos visibles
al salir de la sesión. No usa localStorage para el historial. Los errores y el
éxito del guardado se muestran desde la respuesta de API. Las selecciones visuales
anteriores siguen siendo demostraciones independientes.

## Verificación ejecutada

Con MySQL y Mailpit locales existentes y saludables, sin recrear contenedores.
Los comandos de conexión necesitaron ejecución fuera del sandbox por restricción
de acceso al socket Docker y servicios locales.

Desde la raíz:

```bash
set -a
source .env
set +a
cd backend
PREVIA_TEST_MYSQL=1 .venv/bin/pytest -q
```

Resultado final: **32 passed**, con un aviso de deprecación existente de
Starlette/TestClient con httpx; no se cambiaron dependencias por este aviso.
Incluye las pruebas anteriores de autenticación, persistencia y planificación.
Las seis nuevas cubren sesión, catálogo de 53 asignaturas, tres estados, rechazos,
revisiones completas, recarga mediante un cliente nuevo, reingreso OTP, aislamiento
entre dos cuentas, revisión obsoleta, CSRF/origen, preflight PUT y rollback ante un
fallo de escritura. Los casos H04-A revierten sus datos al terminar; la suite
anterior mantiene su comportamiento de identidades sintéticas de concurrencia.

Otros comandos desde la raíz:

```bash
backend/.venv/bin/ruff check backend
npm run build --prefix frontend
frontend/node_modules/.bin/tsc frontend/src/app/demo/demand-demo.ts frontend/src/app/demo/demand-catalog.ts --outDir /tmp/previa-h01-c --module commonjs --target es2022 --skipLibCheck
node frontend/checks/demand.cjs
git diff --check
```

Ruff: sin errores. Compilación Angular: correcta. Verificación existente de
Demanda: correcta (53 asignaturas, 80 estudiantes sintéticos, 160 intenciones).
No se modificaron sus archivos ni su comportamiento.
git diff --check: sin errores de espacios.
No hubo commits, push, despliegues ni servicios externos.

**Limitación real:** no se ejecutó Firefox ni automatización de navegador.
La recarga y el reingreso están probados contra la API con MySQL; queda pendiente
la comprobación visual y del flujo interactivo en Firefox según los pasos siguientes.
No se comprobó reinicio físico de MySQL en H04-A.

## Demostración en Firefox

Usar los servicios locales existentes según h02-b-authentication.md. Reiniciar la
API para cargar las nuevas rutas si no corre con --reload. No ejecutar seed.

En una terminal desde la raíz:

```bash
set -a
source .env
set +a
cd backend
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-proxy-headers
```

En otra terminal:

```bash
cd frontend
npm start
```

1. Abrir http://127.0.0.1:4200/iniciar-sesion e iniciar sesión con una cuenta de
   prueba del dominio estudiantes.example.test. Obtener el OTP de Mailpit en
   http://127.0.0.1:8025.
2. Abrir la pestaña **Mi perfil académico**, también accesible directamente en
   http://127.0.0.1:4200/mi-perfil-academico.
3. Comprobar la advertencia provisional/no oficial y las 53 materias por semestre.
   En una cuenta nueva todas aparecen sin declaración.
4. Indicar semestre actual declarado y marcar algunas materias como APROBADA,
   REPROBADA o NO CURSADA. Dejar las restantes sin declaración.
5. Pulsar **Guardar perfil académico**. Ver el mensaje de API
   «Perfil académico guardado.» y el número de revisión incrementado.
6. Recargar Firefox: las declaraciones y semestre deben recuperarse de MySQL.
7. Cerrar sesión y volver a entrar con el mismo correo y un nuevo OTP (respetar
   los 60 segundos mínimos entre emisiones). Volver al perfil: conserva los datos.
8. Cambiar una declaración a «Sin declaración (desconocido)», guardar y recargar:
   desaparece de los estados explícitos, pero su revisión anterior sigue en MySQL.
9. Opcional: abrir el perfil en dos pestañas, guardar en una y guardar después en
   la otra. La segunda recibe conflicto y debe usar **Recargar perfil desde MySQL**
   antes de volver a editar.

En Red de Firefox, comprobar GET del catálogo y perfil y PUT del guardado (200),
sin IDs de usuario en el cuerpo. Sin sesión, la consulta de API responde 401.
