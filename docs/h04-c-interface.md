# H04-C — Simplificación visual local

## Alcance confirmado

Se simplificaron Inicio, acceso, registro, verificación OTP, perfil académico,
asignaturas habilitadas, selección de ejemplo, Mi selección, Historial y Demanda.
Se conservan cabecera azul degradada, pestañas horizontales, menú lateral,
colores, fuentes, botones, formularios y tablas compactas. Sin librerías nuevas,
publicación, commits, cambios de API, base de datos ni lógica académica/estadística.

## Cambios de presentación

- Inicio: bienvenida breve y cuatro accesos a las funciones principales.
- Acceso/registro/OTP: formulario primero, ejemplo de correo y ayuda mínima;
  detalles del registro y alcance en «¿Cómo funciona el acceso?». Se conservan
  mensajes de error/estado, etiquetas, ayudas asociadas y validación de campos.
  La vigencia del código sigue apareciendo en el mensaje del servicio existente.
- Perfil: aviso breve, asignaturas por semestre, botón «Guardar perfil» y ayuda
  secundaria desplegable. El aviso de descarte al recargar sigue visible y
  asociado al botón. D03 sigue visible: sin declaración la asignatura se bloquea.
- Elegibilidad: etiquetas breves con causa general del bloqueo, «Ver detalles»
  para motivos y requisitos; se conserva la distinción entre prerrequisitos
  cumplidos y habilitación, y el aviso de autodeclaración no certificada.
- Selección/Mi selección: búsqueda, tablas y prioridades primero. Se retiran
  pasos decorativos y explicaciones repetidas; el carácter temporal del ejemplo
  y los límites 3 altas + 4 medias/bajas siguen visibles. Sin envío de solicitudes.
- Historial: movimientos y acceso a selección; alcance temporal en ayuda.
- Demanda: indicadores, filtros y tablas con identificación sintética visible.
  Metodología en «Acerca de estos datos», reglas por asignatura en «Ver regla».
  La advertencia de grupos orientativos permanece junto al campo de simulación;
  los errores de tamaño inválido no se ocultan. Cálculos y CSV sin cambios.
- Menú: enlaces alineados y selección de ejemplo/leyenda en un desplegable.
  En móvil conserva el botón para abrir el menú y las pestañas desplazables.

Se corrigieron textos antiguos que presentaban autenticación/perfil como futuros.
Las tablas mantienen desplazamiento propio; se corrigió el ancho mínimo del
fieldset que hacía desbordar el formulario académico en móvil.

## Archivos de H04-C

- `frontend/src/app/features/home/home.html` y `home.ts` (visibilidad del acceso
  cuando ya hay sesión).
- `frontend/src/app/features/auth/auth-form.html`, `auth-form.css`,
  `auth-presentation.html`, `auth-presentation.css`.
- `frontend/src/app/features/academic/academic.html`, `eligibility.html` y
  `eligibility.ts` (solo etiquetas visibles en este último).
- `frontend/src/app/demo/demo.html`, `demand.html` y `frontend/src/styles.css`.
- Este documento. Los cambios de H04-B ya presentes no pertenecen a H04-C.

## Verificaciones ejecutadas

Desde `frontend/`, todas con salida 0:

```bash
npm run build
node_modules/.bin/tsc src/app/demo/demand-demo.ts src/app/demo/demand-catalog.ts --outDir /tmp/previa-h01-c --module commonjs --target es2022 --skipLibCheck --ignoreConfig
node checks/demand.cjs
```

La comprobación frontend existente valida prerrequisitos del ejemplo, exclusiones,
deduplicación, filtros, orden, porcentajes, semestres, grupos y CSV. Conserva
53 asignaturas, 80 estudiantes, 160 intenciones, 35 asignaturas con demanda y
53/54/53 prioridades alta/media/baja. No hay un runner `npm test` configurado.

Firefox headless local, mediante WebDriver BiDi y un comprobador temporal:
**49 comprobaciones correctas**, nueve rutas en anchos de 1366, 390 y 320 px.
Incluye renderizado sin desbordamiento de página, menú móvil, ayudas desplegables,
53 estados del perfil y guardado, motivo D03, formularios de acceso/registro y
código, selección y cambio de prioridad, navegación a Mi selección/Historial,
filtros de Demanda y error visible de tamaño de grupo. Se inspeccionaron capturas
de escritorio y móvil. Las tablas conservan desplazamiento horizontal interno.

**Límite:** las respuestas de la API se simularon solo dentro de ese Firefox.
Se comprueba la interfaz, no la entrega SMTP, autenticación real ni persistencia
MySQL. No se escribió en la base. La lógica OTP y los contratos no se modificaron.
La compilación detectó inicialmente una etiqueta de cierre sobrante en la tabla
de Demanda; se corrigió y el build final pasó.

`git diff --check`: salida 0. No hay pendientes funcionales detectados para H04-C.
