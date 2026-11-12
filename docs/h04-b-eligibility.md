# H04-B — Elegibilidad curricular autodeclarada

Implementación local limitada a consulta; sin selección, envío, cambios de
Demanda, autenticación, migraciones ni modificación del catálogo original.

## Confirmado

`GET /api/v1/me/eligibility` requiere la sesión OTP existente. Devuelve 401 sin
sesión, 403 sin perfil de estudiante y 409 `perfil_requerido` si aún no se ha
guardado una revisión académica. Usa la última revisión por número del estudiante
autenticado y exclusivamente sus entradas y aristas en esa versión de malla.
No acepta una identidad ni revisión indicadas por el cliente.

Respuesta 200, con `Cache-Control: no-store`:

- `revision_perfil`, `malla_id`, `base_datos: AUTODECLARADA`, `provisional: true`
  y advertencia general de ausencia de certificación universitaria.
- `materias`: `malla_asignatura_id`, `asignatura_id`, `nombre`,
  `semestre_curricular`, `estado_declarado` (null significa desconocido),
  `seleccionable`, `motivos` con `codigo`, `mensaje` y `requisito_id` cuando aplica.
- Cada materia contiene `prerrequisitos_requeridos`, `prerrequisitos_aprobados`
  y `prerrequisitos_pendientes`: entradas con ambas identidades, nombre y estado.
  Incluye `estado_regla`, `condiciones_externas` y `advertencia` específica nullable.

APROBADA bloquea repetición. Todos los prerrequisitos internos deben estar
APROBADA explícitamente; REPROBADA, NO CURSADA y ausencia no los satisfacen.
La ausencia de aristas solo permite evaluar una regla explícita
`ninguno_explicito_propuesto`, sin revisión pendiente ni condición externa.
Una regla que declara prerrequisitos pero carece de aristas se bloquea también.
Las reglas propuestas calculables siguen siendo provisionales, nunca oficiales.

Esta consulta no depende de oferta, cupos ni ventanas de captura. El parámetro
`period_id` del diseño general no se utiliza en H04-B; no certifica disponibilidad
para un período. Se conserva el contrato base y se añaden los detalles anteriores.

## D03 ratificada

**Confirmado por el usuario:** la candidata sin declaración permanece bloqueada
con `declaracion_incompleta` y «Declara el estado académico de esta asignatura.».
El indicador `prerrequisitos_cumplidos` es independiente de `seleccionable`:
requiere reglas calculables sin incertidumbre y ninguna aprobación faltante.
APROBADA nunca es seleccionable; REPROBADA y NO CURSADA pueden serlo si cumplen
los prerrequisitos y las reglas están suficientemente verificadas.

Ejemplo corregido: Cálculo I y Álgebra Lineal APROBADA, Química I REPROBADA y
Cálculo II sin declaración. Cálculo II tiene sus prerrequisitos cumplidos, pero
**no está habilitada** hasta declarar NO CURSADA o REPROBADA. Física I solo se
habilita si también tiene estado NO CURSADA o REPROBADA. Probabilidad y Estadística
queda bloqueada por Cálculo II sin aprobación; Química II, por Química I REPROBADA.
No se equipara ausencia de declaración a NO CURSADA.

## Interfaz y comprobación en Firefox

Con los servicios locales existentes (MySQL, FastAPI en 8000, Angular en 4200,
Mailpit en 8025), abrir `http://127.0.0.1:4200` en Firefox:

1. Iniciar sesión por el flujo OTP existente y consultar el código en Mailpit.
2. En «Mi perfil académico», declarar Cálculo I y Álgebra Lineal APROBADA,
   Química I REPROBADA. Marcar las candidatas NO CURSADA para comprobar D03.
   Guardar el perfil.
3. Abrir «Asignaturas habilitadas» (`/asignaturas-habilitadas`): aparecen los diez
   semestres y los indicadores Habilitada, Bloqueada por prerrequisitos,
   Ya aprobada y Pendiente de verificación de reglas.
4. Cálculo II y Física I se habilitan. Probabilidad y Estadística y Química II
   quedan bloqueadas. Expandir «Consultar motivos y requisitos» para ver las
   aprobaciones faltantes. Inglés III permanece pendiente de verificación.
5. Guardar una nueva revisión con Cálculo II APROBADA; volver a la vista o pulsar
   «Actualizar elegibilidad». Probabilidad y Estadística se habilita si su estado
   es NO CURSADA/REPROBADA y Álgebra Lineal sigue APROBADA.
6. En Red de Firefox comprobar el GET a `/api/v1/me/eligibility` y su número de
   revisión. Cerrar sesión impide consultar los resultados.

No hay botones para seleccionar o enviar en esta vista. Los cambios sin guardar
en el formulario académico no alteran el resultado del servidor.

## Verificación ejecutada

Desde raíz, cargar `.env` con `set -a`, `source .env`, `set +a` sin imprimirlo.
Desde `backend`:

```bash
PREVIA_TEST_MYSQL=1 .venv/bin/python -m pytest -q --tb=short
.venv/bin/ruff check .
.venv/bin/ruff format --check .
```

Resultado de la suite completa: **41 passed, sin exclusiones ni omisiones**
(incluye 9 casos H04-B y la concurrencia OTP). Se ejecutó dos veces sobre la
misma base: 41 aprobadas en ambas, códigos de salida 0. Ruff correcto.
La prueba concurrente OTP usa conexiones independientes, barreras para iniciar
las dos operaciones y correo/IP únicos por ejecución. Un fixture identifica sus
eventos con una referencia sintética y limpia en `finally` exclusivamente sus
sesiones, roles de usuario, perfil, usuario, desafíos, límites y eventos; comprueba
que no quedan registros propios. No elimina datos preexistentes. El resto de
pruebas académicas conserva rollback por caso. No cambia autenticación funcional.
Advertencia preexistente de Starlette por deprecación de su transporte HTTPX.

Desde `frontend`: `npm run build`, compilación correcta.
`git diff --check`, correcto. Firefox: pasos manuales documentados, no ejecutados.
