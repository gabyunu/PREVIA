# H01-B — Migración visual a Angular 22

Fecha: 2026-11-11.

## Alcance y autorización

**Confirmado:** el usuario autoriza reutilizar la interfaz anterior como referencia
visual obligatoria para H01-B. Esto constituye la excepción explícita a la regla
general de no reutilizar prototipos. Se conservan Angular 22 y sus dependencias.
Se revisaron AGENTS.md, requirements.md, decisions.md, architecture.md, roadmap.md,
los cuatro archivos fuente indicados del prototipo y su preview/ABRIR_DEMO.html.
Los textos antiguos de fase 0 no amplían ni bloquean esta autorización específica.
H02 continúa sin autorización.

**Implementado:** Inicio, Selección de asignaturas, Mi selección, Historial y
Demanda, con rutas locales y navegación superior/lateral. Se reaprovecha el
componente Inicio; el contenedor visual, el fixture sintético y el estado efímero
se separan en app/demo/. La selección conserva sus cambios al navegar y los pierde
al recargar. No utiliza localStorage, API, autenticación ni base de datos.

El fixture fija ejemplos de estados declarados y de prerrequisitos para presentar
las filas seleccionables y bloqueadas. No es un evaluador curricular. Sus cifras,
créditos, códigos, nombres y semestres son ficticios. La vista Demanda tiene conteos
estáticos por prioridad y no incorpora los cambios de la selección local.
La revisión muestra un mensaje; no simula haber guardado o enviado una solicitud.
Los límites de prioridades en esta demostración no sustituyen validaciones futuras
en backend.

**Pendiente:** datos institucionales, integración y reglas de negocio de los hitos
correspondientes. No se adoptan decisiones técnicas pendientes por esta migración.

## Fidelidad y diferencias respecto al original

Se parte del CSS original: cabecera degradada de 123 px en escritorio, marca PREVIA,
Arial/Helvetica, pestañas horizontales, menú lateral de 180 px, barras degradadas,
tablas compactas, botones, formularios y avisos. No se agrega biblioteca visual.
Se usa el mismo componente contenedor en todas las rutas.

Diferencias necesarias por V1 y por el alcance de H01-B:

- Se reemplazan reconfirmación y etiquetas de oferta/elegibilidad oficial por
  navegación y textos coherentes con declaración de interés.
- No se muestran capacidades, brechas ni horarios. Demanda muestra alta/media/baja
  y total sintético, con advertencias sobre autodeclaración.
- El período y la malla se etiquetan DEMO; no se conserva el calendario del prototipo.
- No hay selector de rol, envío, retiro, exportaciones o modal de confirmación.
  Solo hay revisión visual e historial temporal de interacciones.
- Las cinco pantallas aparecen en las pestañas. Su ancho y los avisos de demostración
  cambian respecto al original; no se ofrece una reproducción píxel a píxel.
- En móvil la cabecera crece a 148 px, las pestañas admiten desplazamiento horizontal
  y el menú lateral se convierte en un desplegable. El prototipo ocultaba ese menú.
  Las tablas mantienen desplazamiento horizontal para conservar su formato compacto.
- Se añaden foco visible, enlace para saltar al contenido, etiquetas para controles
  repetidos y regiones de tablas accesibles mediante teclado.

**Pendiente de revisión manual:** apariencia renderizada y recorrido con teclado
en escritorio y móvil. No se ejecutó una comparación visual en navegador.

## Archivos

Creados:

- frontend/src/app/demo/demo.ts y demo.html: contenedor y pantallas de demostración.
- frontend/src/app/demo/demo-data.ts: fixture sintético sin datos institucionales.
- frontend/src/app/demo/demo-state.ts: selección e historial solo en memoria.
- docs/h01-b-migration.md: esta entrega y sus verificaciones.

Modificados:

- frontend/src/app/app.routes.ts: cinco rutas y retorno a Inicio para rutas desconocidas.
- frontend/src/app/app.ts: formato del componente raíz existente.
- frontend/src/app/features/home/home.ts y home.html: Inicio con la estética original.
- frontend/src/styles.css: estilos de referencia y adaptación de navegación móvil.
- frontend/src/index.html: título y formato.
- docs/local-development.md y docs/roadmap.md: ejecución y estado de H01-B.

Backend, endpoint /health, dependencias, archivos de bloqueo y originales de
referencias/ no se modificaron. Los archivos no rastreados que ya existían en
referencias/ se conservaron.

## Verificaciones reales

- En frontend/: `npm run build`: exit 0. Build final de producción: 306.08 kB
  iniciales y 82.27 kB de transferencia estimada. Salida: dist/previa/browser/.
- No existe script npm test ni pruebas frontend configuradas en H01. No se añaden
  dependencias ni se afirma haber ejecutado pruebas de navegador.
- En backend/: `.venv/bin/python -m pytest -q`: **1 passed in 0.27s**, exit 0.
- `.venv/bin/ruff check .`: **All checks passed!**, exit 0.
- `.venv/bin/ruff format --check .`: **6 files already formatted**, exit 0.
- `git diff --check`: exit 0.
- Comparación SHA-256 antes/después de 25 archivos de backend/ y referencias/,
  excluyendo entorno virtual y cachés: sin diferencias ni archivos fuente nuevos.

Incidencias: el primer build se lanzó desde la raíz y falló por ausencia de
package.json; se corrigió a frontend/. El sandbox emite `Failed to create stream
fd` y bloqueó pytest; se interrumpió ese intento y se repitieron las verificaciones
backend con permisos ampliados, con los resultados anteriores.

## Abrir la interfaz

Con las dependencias existentes, desde la raíz:

```bash
cd frontend
npm start
```

Abrir http://127.0.0.1:4200. No requiere iniciar FastAPI. Detener con Ctrl+C.
Rutas: /, /seleccion, /mi-seleccion, /historial y /demanda.

Recorrido manual recomendado: agregar DEMO201, cambiar su prioridad, navegar a
Mi selección e Historial, filtrar por código/semestre, comprobar filas bloqueadas,
visitar Demanda y recargar para comprobar el reinicio del estado temporal. Repetir
con una ventana pequeña y desplegar Opciones y enlaces.
