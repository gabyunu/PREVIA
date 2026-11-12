# H07 — Historial real de solicitudes

## Alcance y revisión previa

**Confirmado:** solo lectura del historial propio autenticado desde MySQL.
Historial anterior mostraba `DemoState.events()` en memoria, con datos sintéticos;
se reemplazó su contenido por un componente independiente. No se usa ese fixture
como respaldo cuando la API falla. Se conservan cabecera, navegación, colores y CSS;
solo cambian contenido y rótulos específicos de Historial. El piloto sigue usando
datos demostrativos, pero sus solicitudes son persistidas y están separadas de los
movimientos sintéticos en memoria de otras vistas.

Se revisaron AGENTS.md, requisitos, decisiones, arquitectura, roadmap, modelos,
migraciones 0001–0007 y Git. Había cambios H05/H06 y referencias sin commit; se
conservaron. El antiguo roadmap llamaba H07 a revalidación: esta entrega usa la
definición explícita del usuario, historial, sin ampliar reglas.

Reutiliza `solicitud`, `version_solicitud`, `detalle_solicitud`,
`evento_solicitud`, `periodo_academico`, perfil y entradas curriculares.
No necesita migración, ni tablas nuevas, ni reescritura de históricos.
Dependencias: sesión H02-B, versiones H05-A/B, catálogo y MySQL migrado.
Riesgo principal: confundir trabajo pendiente con envío vigente. Se exponen ambos
punteros y se clasifican las versiones por eventos, sin inferir vigencia del número
más alto. Aceptación: permisos propios, períodos separados, versiones y prioridades
inalteradas, persistencia tras logout/login y regresión aprobada.

## Contrato de lectura

Todos requieren sesión válida y perfil estudiantil. La identidad se deriva solo
de la sesión; no reciben identificador estudiantil. Recursos ajenos o inexistentes
responden 404 indistinguible; ausencia de sesión devuelve 401. Respuestas sin datos
personales ni fundamento académico completo, con `Cache-Control: no-store`.

- `GET /api/v1/me/request-history?offset=0&limit=10`: principales propias ordenadas
  por inicio de período descendente e ID, una por período; total y página. Incluye
  período, estado principal, creación, último envío explícito, punteros y resumen
  de trabajo actual, vigente o última versión conservada, en ese orden.
- `GET /api/v1/me/request-history/{request_id}/versions?offset=0&limit=10`:
  principal y versiones por número descendente; total y página independientes.
- `GET /api/v1/me/request-history/{request_id}/versions/{version_id}`:
  detalle de versión propia con asignaturas, semestres, prioridades originales,
  malla/revisión originales, registro, eventos, tipo, estado y vigencia actual.

`limit` entre 1 y 50; `offset` no negativo. La interfaz usa 10 por página.
El detalle está limitado por las selecciones de la versión (máximo operativo 7).
Los borradores previos siguen consultables aunque nunca fueran enviados.
`enviada` identifica envío explícito o renovación compatible de fundamento;
`vigente` procede exclusivamente del puntero existente. Versiones antiguas se
muestran sustituidas, salvo invalidación registrada, que se presenta explícita.
Un borrador actual puede coexistir con principal enviada y envío vigente.

**Recomendado y adoptado:** creación de la principal = mínimo `creado_en` de sus
versiones, porque la tabla principal no almacena fecha propia. No se inventa un
campo retrospectivo. Envío = evento `envio`; una renovación de fundamento no
inventa otra fecha de envío. Fechas almacenadas UTC, presentadas como horas locales.

El detalle reutiliza `drafts.version_data`: instantánea de nombre y semestre del
fundamento enviado cuando existe; si no existe (borradores o registros anteriores),
entrada de la malla original referenciada, nunca la malla del perfil actual.
**Limitación existente:** no se pueden reconstruir etiquetas antiguas si alguien
alteró manualmente una entrada curricular de un borrador sin instantánea; se
mantiene la política de publicaciones inmutables, sin inventar datos faltantes.

No se modifica autenticación, evaluación, Demanda, envío, invalidación ni cierre.
No se implementa retiro/reconfirmación. El frontend elimina resultados al cambiar
sesión e ignora respuestas tardías; no conserva historial en localStorage.

## Archivos H07

Nuevos: `backend/app/history.py`, `backend/tests/test_history.py`,
`frontend/src/app/features/academic/history.ts` y `history.html`,
`frontend/checks/history.cjs`, esta guía.
Modificados: registro del router en `backend/app/main.py`, integración de Historial
en `frontend/src/app/demo/demo.ts/html`, notas de alcance en requirements,
decisions, architecture y roadmap. Los demás cambios que muestra Git son previos.

## Verificación real

- MySQL de trabajo: `PREVIA_TEST_MYSQL=1 .venv/bin/pytest -q tests/test_history.py
  --tb=short`: **3 passed**, cubren permisos, aislamiento, dos períodos, paginación,
  correcciones y versiones, prioridades originales, instantánea de nombre/semestre,
  renovación e invalidación, logout/login, períodos no publicados y parámetros.
- Regresión inicialmente en base de trabajo: **72 passed, 10 failed**. Las pruebas
  antiguas usan conteos globales y suponen ausencia de perfiles/solicitudes ajenos;
  había registros previos. No se eliminaron ni se reinicializó MySQL.
- Se creó la base separada `previa_h07_verification` en el MySQL local, se ejecutó
  `.venv/bin/alembic upgrade head` y `.venv/bin/python -m app.db.seed` exclusivamente
  allí. Con `MYSQL_DATABASE=previa_h07_verification`,
  `PREVIA_TEST_MYSQL=1 .venv/bin/pytest -q --tb=short`: **82 passed**, sin skips.
  Advertencia preexistente de Starlette/TestClient sobre httpx.
- `.venv/bin/alembic check`: **No new upgrade operations detected**, tanto en la
  base de trabajo como en la separada.
- `.venv/bin/ruff check .`: aprobado.
- `npm run build`: aprobado.
- `node checks/history.cjs`: paginación, detalle, prioridades, errores, respuestas
  fuera de orden y limpieza/cambio de sesión aprobados.
- `node checks/submit.cjs`, `node checks/demand-real.cjs`: aprobados.
- Compilación TypeScript de selection-rules y `node checks/selection.cjs`: aprobado.
- Compilación TypeScript de demand-demo/demand-catalog y `node checks/demand.cjs`:
  aprobado; fixture H01-C sin cambios.
- `git diff --check`: aprobado.

Primer intento MySQL bloqueado por sockets del sandbox y ruta `.env` equivocada;
corregida a `../.env` y ejecución autorizada local. Primer intento de crear el
comprobador frontend usó ruta duplicada; se corrigió. Su primer error por `Error`
de otro contexto VM se corrigió compartiendo el constructor en el comprobador.
Ruff format corrigió líneas largas antes de la pasada final.
Sin dependencias nuevas, commits, push, despliegues ni servicios externos.
La base separada queda disponible para verificaciones; no se eliminó.

## Revisión desde Firefox

1. Mantener MySQL y Mailpit locales, API en `http://127.0.0.1:8000` con `.env`
   habitual y frontend con `npm start` desde `frontend/`. Si la API no usa recarga,
   reiniciarla para registrar las rutas H07. No apuntar la aplicación de trabajo
   a la base separada de verificación.
2. En Firefox abrir `http://127.0.0.1:4200/historial`; sin sesión muestra acceso.
   Iniciar sesión OTP habitual, usando Mailpit local `http://127.0.0.1:8025`.
3. Ver solicitudes por período; si no existen, guardar un borrador desde Mi
   selección durante captura abierta usando datos del piloto. Volver a Historial
   y pulsar Actualizar historial. No se crean solicitudes ficticias al consultar.
4. Pulsar Ver versiones y Ver asignaturas. Comparar número, malla, semestre y
   prioridades. Tras enviar con el flujo existente, actualizar: aparece vigente.
5. Guardar corrección de prioridad: quedan visibles borrador y envío vigente.
   Enviar corrección, actualizar y abrir versión anterior: conserva su prioridad
   original y aparece sustituida. Navegar páginas si hay más de diez registros.
6. Cerrar sesión y volver a iniciar: persiste el mismo historial. Con otra cuenta
   o ventana privada solo aparecen sus propias solicitudes; URLs de recursos
   ajenos en Red devuelven 404, sin información personal.
7. En Red verificar los tres GET de esta guía, cookies de sesión y respuesta
   `no-store`. La pantalla no realiza escrituras de solicitudes.

**Pendiente:** recorrido visual manual Firefox. Build y comprobadores automatizados
no equivalen a una inspección visual. Dominios, fechas, mallas institucionales y
políticas de privacidad/retención continúan pendientes y fuera de H07.
