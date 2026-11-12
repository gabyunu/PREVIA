# PREVIA — API REST preliminar

## Alcance vigente H04-A

**Confirmado y autorizado:** perfil académico propio con sesión OTP, catálogo de las
53 asignaturas del piloto, estados autodeclarados y revisiones completas en MySQL.
Esta autorización sustituye las restricciones históricas de implementación
únicamente para H04-A. Véase [contrato, verificación y demostración](h04-a-academic-profile.md).
**Recomendado y adoptado localmente:** control de revisión esperada y bloqueo del
perfil; lectura excepcional del borrador piloto sin publicarlo.
**Pendiente:** D11 para cambios de carrera/malla, fuentes oficiales, privacidad
institucional, elegibilidad, solicitudes, administración y reportes persistidos.
No se amplía el alcance a esos servicios.


## Alcance específico H02-C

**Confirmado e implementado:** persistencia aditiva de períodos, planificación de
cupos y notas administrativas, más fuente/fecha de revisión de reglas curriculares.
La autorización actual se limita a H02-C y conserva H02-A/H02-B; las menciones
históricas a fase 0 o autorización pendiente no describen esta entrega.
Véanse [tablas, límites, reportes futuros y evidencia H02-C](h02-c-planning.md).
Cupos orientativos no constituyen oferta ni condicionan selección; NULL o ausencia
significa desconocido, cero es explícito. Sin nuevas APIs ni cambios visuales,
de autenticación o de las 53 asignaturas. Solicitudes y reportes reales siguen
**pendientes**, al igual que servicios administrativos y datos institucionales.

## Estado de implementación H02-B

El usuario autorizó autenticación **solo local** con OTP, Mailpit, sesiones y
conexión Angular. Está implementada y verificada según
[alcance, configuración y evidencia H02-B](h02-b-authentication.md).
Las notas históricas sobre fase 0, ausencia de endpoints o H02-B pendiente se
limitan al estado anterior. No se autoriza perfil académico ni hitos posteriores.
Los dominios oficiales, privacidad/retención y administración siguen pendientes.

**Recomendado; sin endpoints implementados.** Prefijo propuesto /api/v1. Referencias
D01–D06 confirmadas; recomendaciones locales y pendientes D07–D13 en planning-review.md. IDs opacos en contratos; fechas ISO 8601 con zona.
Instantes normalizados a UTC y zona IANA configurable; validar zona y orden de
ventana anterior al semestre destino sin inferir un calendario oficial.
Listados paginados con límite máximo configurable y orden estable. Pydantic rechazará
campos no previstos, duplicados y prioridades desconocidas. Nunca aceptar estudiante,
rol, aprobaciones de servidor o estado enviado arbitrario en un cuerpo de selección.

## Identidad y permisos

| Método / ruta | Entrada mínima | Salida / autorización |
|---|---|---|
| POST /auth/otp/request | correo | 202: mensaje genérico, desafio_id opaco; mismo formato para cuentas inexistentes/no admitidas |
| POST /auth/otp/verify | desafio_id, codigo | 200: usuario {id, roles}, cookie de sesión; crea estudiante si primer acceso, accede al existente; 401 genérico en fallo |
| POST /auth/logout | Sin cuerpo; protección CSRF | 204, revoca sesión y cookie |
| GET /me | Sesión | 200: id, correo propio, roles; no otros usuarios |
| GET /health | Sin sesión | 200 disponibilidad mínima; sin configuración sensible |

OTP mal formado: 422; tasa excedida: 429 con Retry-After, sin revelar existencia de
cuenta. Verificación fallida no distingue vencido, consumido, inexistente o incorrecto.
Cookies y token CSRF según architecture.md; rol solo calculado por servidor. Consumo OTP, creación de usuario/identidad de estudiante y sesión son atómicos; UNIQUE de correo evita cuentas duplicadas. El perfil curricular se completa después. Sin endpoint público de alta o promoción administrativa.

## Perfil, catálogo y elegibilidad

| Método / ruta | Entrada / filtro | Salida / permiso |
|---|---|---|
| GET /careers | Paginación | Catálogo publicado, sesión |
| GET /curricula?career_id=… | Carrera | Versiones publicadas, sesión |
| GET /curricula/{id} | ID | Asignaturas {malla_asignatura_id, asignatura_id, codigo_publicado, nombre_publicado, semestre_curricular}, aristas {asignatura_id, requisito_id}, versión; sesión |
| GET /me/academic-profile | Sesión | revision, malla_id, semestre_declarado, estados explícitos; ausencia marcada como sin declaración |
| PUT /me/academic-profile | revision_esperada, malla_id, semestre_declarado, estados [{malla_asignatura_id, estado}] | Nueva revisión, solicitudes_afectadas [{id, estado, motivos}]; solo dueño |
| GET /periods | Filtros publicados | Períodos destino, inicio_periodo, captura_desde/hasta, zona_horaria, captura_abierta calculada |
| GET /me/eligibility?period_id=… | Período | revision_perfil, materias [{malla_asignatura_id, asignatura_id, seleccionable, motivos [{codigo, requisito_id?}]}] |

PUT reemplaza la declaración completa de esa revisión, no es un parche ambiguo:
una entrada omitida vuelve a ausencia desconocida (D03 confirmada), nunca a aprobada ni no cursada. Rechazar estados fuera de las
tres categorías. La revisión esperada impide sobrescribir otro cambio. D04/D11
rigen efectos del cambio; D04 exige excluir toda solicitud incompatible en la misma transacción y conservar la instantánea tras cierre. D11 sigue pendiente para cambios de carrera/malla; estado aprobado nunca se deduce del semestre.

## Solicitud única por período

| Método / ruta | Entrada | Salida |
|---|---|---|
| GET /me/requests/{period_id} | Sesión | 200 estado, revision_control, vigente y trabajo con sus IDs/detalles; 404 si no existe |
| PUT /me/requests/{period_id}/draft | revision_esperada (0 si nueva), revision_perfil, selecciones [{malla_asignatura_id, prioridad}] | 200 nueva revisión de trabajo, estado principal, advertencias y vigente preservada |
| POST /me/requests/{period_id}/submit | Cabecera Idempotency-Key; revision_esperada, version_trabajo_id, revision_perfil | 200 enviada, version_vigente_id, revision_control; valida todo de nuevo |
| POST /me/requests/{period_id}/withdraw | revision_esperada | 200 retirada, vigente nula, revision_control |
| POST /me/requests/{period_id}/recover | revision_esperada | 200 borrador con nueva revisión de trabajo y advertencias; no envía |
| GET /me/requests/{period_id}/history | Paginación | Versiones y eventos propios, sin secretos ni datos ajenos |

Prioridad ∈ {alta, media, baja}; máximo 3 altas, 4 medias/bajas, 7 total; mínimo de
envío: una asignatura de cualquier prioridad (D02 confirmada), sin altas obligatorias. El servidor usa dueño de sesión y período de ruta. version_trabajo_id
ajena se rechaza. Respuestas incluyen marca de autodeclaración y motivos por materia.
**Idempotencia recomendada de submit:** el cliente genera una clave aleatoria opaca
(UUID) por intención de envío y conserva clave y cuerpo hasta conocer el resultado.
Reintenta con la misma clave y cuerpo tras un error de conexión. Backend exige
`Idempotency-Key` (ausente/formato inválido: 422), acotada a usuario autenticado y
período. No reutilizar una clave para otra intención.

Tras autenticar y autorizar, tomar bloqueos perfil → período → solicitud; consultar
el registro de clave **antes** de comprobar revisión esperada, ventana y estado.
Si existe y coincide la huella, devolver el mismo 200 y cuerpo del éxito original,
sin mutar, incrementar revisiones ni crear eventos. Funciona aunque después se haya
retirado, invalidado o cerrado: describe el resultado de aquella operación, no
restaura vigencia. Para estado actual, consultar GET. Misma clave con otro cuerpo:
409 `clave_idempotencia_reutilizada`. Sin registro, aplicar todas las validaciones
actuales y guardar éxito y respuesta en la misma transacción del envío. Un rollback
no deja registro ni efectos; errores de validación no se memorizan. Bloqueos y UNIQUE
serializan reintentos concurrentes; tras esperar, consultar de nuevo la clave.

Una clave nueva con revisión obsoleta devuelve 409, incluso si apunta a una versión
antes enviada; nunca sortea control de revisiones. Una respuesta perdida tras commit
se recupera por clave; si no hubo commit el reintento se evalúa normalmente y podría
ser rechazado por cierre o cambio académico. Guardar borrador repetido puede crear
otra revisión, pero nunca otra principal ni alterar vigencia previa. La idempotencia
propuesta se limita a submit en v1.

## Administración propuesta

Todas estas rutas requieren rol preasignado, validación en backend y auditoría.

| Método / ruta | Contrato mínimo |
|---|---|
| POST /admin/careers | codigo, nombre → id; datos sintéticos o autorizados |
| POST /admin/subjects | identificador_catalogo, nombre → id |
| POST /admin/curricula | carrera_id, codigo_version → borrador |
| PUT /admin/curricula/{id}/content | revision_esperada, materias [{asignatura_id, semestre_curricular}], requisitos [{asignatura_id, requisito_id}] → revisión; solo borrador |
| POST /admin/curricula/{id}/publish | revision_esperada → publicada tras validar referencias/ciclos |
| POST /admin/periods | identificador, inicio_periodo opcional en borrador, captura_desde/hasta, zona_horaria → borrador |
| PUT /admin/periods/{id} | revision_esperada, inicio_periodo, ventana y etiqueta → revisión; solo borrador |
| POST /admin/periods/{id}/publish | revision_esperada → publicado; exige inicio_periodo, desde < hasta < inicio_periodo y ahora < inicio_periodo; congelar configuración es propuesta técnica |
| GET /admin/reports/demand | period_id obligatorio; filtros prioridad, malla, semestres; agrupaciones permitidas → filas y metadatos |
| GET /admin/reports/demand.csv | Mismos filtros → CSV agregado, Content-Disposition, metadatos de período/generación |

Las revisiones administrativas usan revision_control en version_malla y
periodo_academico, según la propuesta de data-model.md. No hay borrado de publicados ni reapertura administrativa
propuestos. D06 excluye reaperturas excepcionales de v1. D05 excluye contratos de oferta independiente en v1.

Fila de reporte: version_malla_id, malla_asignatura_id, asignatura_id, codigo_publicado,
nombre_publicado, prioridad, cantidad_estudiantes y dimensiones solicitadas.
La clave de agrupación siempre conserva versión y entrada curricular, incluso sin filtro de malla.
Repetición declarada: estado reprobada en la revisión del envío; no_cursada significa
sin repetición declarada. No expresa número de intentos ni repetición oficial. Metadatos: periodo_id, generado_en, filtros, total_selecciones,
participantes_distintos del mismo universo filtrado, base_datos=autodeclaracion,
advertencia. Cantidades son enteros no negativos; grupos sin selecciones pueden
omitirse, decisión de presentación por revisar. No incluir elegibilidad oficial.

## Errores, concurrencia y límites

Formato propuesto: {error: {codigo, mensaje, campos?, materias?, revision_actual?}}.
Nunca incluir trazas internas, correos de otros usuarios ni OTP.

- 401 sesión ausente/caducada; 403 rol insuficiente; 404 recursos ajenos o inexistentes.
- 409 revision_obsoleta, captura_cerrada o transicion_invalida; operaciones atómicas.
- 422 seleccion_invalida, limites_prioridad, prerrequisitos_incumplidos,
  declaracion_incompleta o minimo_no_cumplido (D02 confirmada).
- 429 límites de emisión/intentos/consulta; 503 correo local temporalmente no disponible,
  sin revelar existencia de usuario.

El backend comprueba hora, rol, estado, dueño y revisión aunque el cliente los haya
validado. Rechazar mutaciones de solicitudes fuera de ventana sin envío automático.
PUT del historial posterior al cierre conserva intacta la instantánea del período. Límites de
paginación/cuerpo/exportación se fijarán con pruebas sintéticas en fases posteriores.


## Precisiones de contrato pendientes de aprobación técnica

- Usar malla_asignatura_id en estados y selecciones; asignatura_id es identidad de
  catálogo informativa en lecturas/reportes. Las aristas del catálogo identifican
  asignaturas dentro de la malla consultada. Rechazar referencias de otra malla con
  422 fuera_de_malla incluso en borrador; no reinterpretar IDs al publicar otra malla.
- GET de solicitud devuelve vigente y trabajo por separado, cada uno con su
  revision_perfil y detalles. Guardar sobre enviada devuelve estado enviada y la
  misma vigente; el nuevo trabajo no cuenta. Submit exitoso devuelve trabajo nulo;
  un fallo no altera ninguno. Withdraw/invalidación devuelven vigente nula y trabajo
  conservado si existe. Recover aplica la regla de copia de data-model.md.
- PUT de perfil permite elegir una malla inicial; se recomienda 409 cambio_malla_no_habilitado
  si intenta cambiarla posteriormente, hasta resolver D11. Una malla activa por
  perfil en v1; publicar otra no activa una migración. Cambios de estados dentro de
  la misma malla siguen D04. Renovar un envío compatible preserva trabajo pendiente;
  submit exige perfil actual y revalidación completa.
- Reportes y CSV leen etiquetas curriculares publicadas, nunca nombres actuales del
  catálogo. No fusionar filas de versiones distintas; consolidación por equivalencias queda fuera de v1. Formato final sigue recomendado bajo D13.
- Los límites son independientes: altas≤3, medias+bajas≤4 y total≤7; no transferir
  capacidad no usada de altas. 1+6 y 0+5 se rechazan tanto al guardar como al enviar.
