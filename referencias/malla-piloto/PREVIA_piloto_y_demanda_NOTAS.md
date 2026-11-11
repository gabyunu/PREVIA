# PREVIA — Alcance de piloto y sección Demanda (propuesta de trabajo)

## Procedencia y estado

- Basado en los 53 nombres de asignaturas y los prerrequisitos propuestos por el usuario.
- **No** es una malla oficial verificada. El nombre y la versión institucional de la carrera siguen sin confirmación.
- Una única carrera en la base de datos del piloto; conservar separación lógica por versión de malla y período académico para historial y reportes.
- Datos personales, registros de solicitudes y cifras del frontend de demostración deben ser siempre sintéticos hasta que exista infraestructura y permisos adecuados.
- El archivo `PREVIA_malla_piloto_propuesta.json` contiene las 53 asignaturas por semestre, textos originales y referencias entre materias; `Pxx-yy` son identificadores internos temporales, nunca códigos institucionales.

## Reglas curriculares pendientes

- `Ninguno` y `Ninguno identificado` NO significan lo mismo: las cinco entradas «Ninguno identificado» requieren validación.
- Nueve asignaturas de itinerario (I–IX): su selección y elegibilidad dependen de la definición del itinerario concreto.
- `Inglés III` remite a `Inglés II*`, asignatura fuera de la malla presentada. No suponer equivalencia ni dar por cumplido el prerrequisito; el asterisco no fue explicado.
- `Proyecto de Titulación I`, `Redacción de Proyecto de Investigación` e `Integración Profesional y Social` mantienen requisitos por verificar.
- Si una regla se desconoce o no se puede evaluar, no etiquetar «elegible» en forma concluyente; mostrar pendiente de verificación. En la demostración, no permitir envío válido real.
- Los prerrequisitos múltiples explícitos requieren aprobación de TODOS (AND), y las aprobaciones se basarán en estados autodeclarados, no certificados institucionalmente.
- No inferir códigos oficiales, equivalencias, correquisitos, cupos, paralelos, oferta de un período ni horarios.

## Cambios visuales mínimos en «Demanda»

Mantener la estética de la referencia original (cabecera azul, pestañas, menú lateral, barras y tablas compactas). Modificar solo el contenido y los controles de la vista Demanda, y los datos sintéticos necesarios para demostrar sus cálculos. Ningún rediseño general.

### Filtros

- Período destino, si existen datos sintéticos para más de uno; versión de malla si hay más de una. En el piloto inicial puede existir solo una opción.
- Asignatura (búsqueda), semestre curricular, prioridad; opcionalmente ordenar por demanda.

### Tarjetas o indicadores pequeños

1. Estudiantes **únicos** con solicitud vigente, válida y enviada (no sumar sus asignaturas como estudiantes).
2. Número de asignaturas con demanda > 0.
3. Total de intenciones válidas de asignatura (suma de selecciones; distinto de personas únicas).
4. Asignatura con mayor demanda, si hay datos.

### Tabla principal por asignatura y versión de malla

- Semestre curricular, asignatura (código institucional solo si está disponible), total de personas que la solicitaron, prioridad alta / media / baja, estudiantes que declararon haberla reprobado, y porcentaje de prioridad alta sobre la demanda de ESA asignatura (`alta / total * 100`, si total > 0).
- Ningún estudiante-asignatura debe contarse más de una vez por solicitud enviada vigente.
- Puede incluir un ordenamiento por demanda total y un resumen por semestre.
- No incluir «capacidad real», «vacantes disponibles», «participación institucional», ni «porcentaje de estudiantes de la carrera» si no se dispone de fuentes y denominadores verificados.

### Simulador opcional de grupos

- Un campo ajustable «Tamaño de grupo de referencia (simulación)», validado como entero positivo.
- Calcular `grupos_orientativos = ceil(demanda_total / tamaño_referencia)` exclusivamente si el parámetro se ha introducido; mostrar que no son grupos oficiales ni cupos autorizados.
- En el piloto no hay información de docentes, aulas, horarios, oferta institucional ni se aprueban aperturas automáticamente.
- No confundir «grupos sugeridos» con «cupos disponibles».

### Exportación

CSV de los valores agregados de la vista filtrada, con período, identificador de versión, asignatura, semestre, total, altas, medias, bajas, repetición autodeclarada y, si corresponde, escenario de grupos. No exportar información personal identificable.

### Reglas de cómputo definitivas para la futura API

- Solo contar versiones actuales válidas de solicitudes enviadas del período elegido. Borradores, solicitudes retiradas/invalidadas y reintentos idempotentes no cuentan.
- Las solicitudes de períodos de captura cerrados se conservan históricamente conforme a las decisiones previas.
- La prioridad alta tiene máximo 3 cursos, y media/baja comparten un máximo conjunto de 4; no alterar estas reglas.
- Separar por versión de malla sin deducir equivalencias por nombre. En una sola versión activa no mostrar un selector redundante si afecta el diseño.
- Toda métrica actual es solo ilustrativa hasta conectarla con la API y MySQL; no usar constantes de un solo registro como si fueran estadísticas institucionales.

## Alcance inmediato de Codex

1. Adaptar SOLO la vista `Demanda` del frontend actual en Angular 22, preservando el resto del aspecto visual.
2. Incorporar los 53 registros a un catálogo sintético de demostración **solo si resulta necesario para mostrar filtros y resultados**. Si hay agregados sintéticos, etiquetarlos como simulados y mantenerlos consistentes matemáticamente.
3. Guardar este insumo en `referencias/`, documentar pendientes y mantener el backend sin cambios en esta tarea.
4. `npm run build` y pruebas disponibles; no instalar MySQL ni modificar migraciones; no hacer commit ni push.
5. Preparar la futura carga de la malla como fixture/seed en H02, sin presentar estos datos como oficiales.
