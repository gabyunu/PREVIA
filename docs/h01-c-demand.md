# H01-C — Demanda estadística de demostración

Autorizado específicamente por el usuario. Solo frontend local, sin backend,
persistencia, H02, instalaciones, servicios externos ni commits.

## Entrega

Se sustituye el contenido de Demanda por un componente aislado. Cabecera,
pestañas, menú lateral y estilos de tablas existentes se conservan; únicamente
se añade ajuste de controles de Demanda para permitir varias líneas.

- Catálogo: copia íntegra de las 53 asignaturas del JSON del usuario en
  `frontend/src/app/demo/demand-catalog.ts`; IDs temporales, nunca oficiales.
- Fixture determinista independiente de DemoState: 96 registros sintéticos,
  80 enviados vigentes, cuatro versiones no vigentes y doce registros
  borrador/retirada/invalidada. Dos selecciones por envío válido en este fixture.
- Validación ilustrativa: requisitos directos AND aprobados, candidata no
  aprobada, reglas calculables, límites de prioridades y solicitud completa.
  No es autorización ni reemplazo de controles futuros del servidor.
- 53 filas, incluidas materias sin demanda. Las reglas pendientes no producen
  demanda válida; cero no implica ausencia de interés real.
- Filtros por búsqueda, semestre curricular y prioridad. Un período y una
  versión explícitos, sin selectores redundantes. Orden ascendente/descendente,
  nombre y semestre. Indicadores y resumen usan el mismo universo filtrado.
- Repetición significa reprobación declarada, sin número de intentos.
- Grupos opcionales: ceil(total/tamaño), entero positivo seguro. Sin capacidad
  institucional, oferta ni apertura de cupos. Campo vacío no calcula grupos.
- CSV UTF-8 BOM, comillas escapadas, neutralización de fórmulas, período,
  versión, filtros, instante UTC, condición curricular y escenario simulado.
  Exporta las filas agregadas filtradas en el orden visible, sin identidades.

## Verificación ejecutada

Desde la raíz:

```sh
frontend/node_modules/.bin/tsc frontend/src/app/demo/demand-demo.ts frontend/src/app/demo/demand-catalog.ts --outDir /tmp/previa-h01-c --module commonjs --target es2022 --skipLibCheck
node frontend/checks/demand.cjs
git diff --check
```

Desde `frontend/`: `npm run build`.

Todos terminaron con código 0. Angular produjo el bundle local (334.85 kB
sin comprimir). El entorno imprimió avisos «Failed to create stream fd»,
sin impedir la compilación.

Resultado del fixture sin filtros: **80 estudiantes únicos**, **160 intenciones**,
**35 asignaturas con demanda**; prioridades **53 altas + 54 medias + 53 bajas**;
**40 repeticiones declaradas**. Las 18 asignaturas restantes tienen reglas
pendientes y se mantienen visibles sin conteo válido sintético.

Los checks verifican catálogo, límites, prerrequisitos, exclusión de estados y
versiones, deduplicación, suma de prioridades, porcentajes, filtros de prioridad
y semestre, ausencia de resultados, orden, suma por semestre, validación del
tamaño y estructura de CSV sin identificadores de estudiantes.

## Estado y pendientes

**Confirmado:** alcance de H01-C y uso exclusivo de datos sintéticos. No se
modifican otras demostraciones ni se conectan con estos resultados.

**Propuesto:** catálogo y prerrequisitos del insumo; no malla oficial.

**Pendiente:** nombre/version institucional, cinco «Ninguno identificado», nueve
itinerarios, Inglés II externo y asterisco, requisitos de titulación,
investigación e integración. No se suponen cumplidos. Revisar visualmente en
navegador y comprobar descarga con una hoja de cálculo: no se ejecutaron esas
comprobaciones manuales. H02 e integración real siguen fuera de alcance.
