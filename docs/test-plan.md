# PREVIA — Plan de verificación

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

**Recomendado.** Son pruebas futuras; no se han ejecutado pytest, Ruff, Angular,
MySQL ni servicios en fase 0. No hay código aplicativo que verificar. D01–D06 de planning-review.md ya fijan expectativas funcionales. Las recomendaciones locales D07–D13 y
los pendientes institucionales se distinguen en planning-review.md; mecanismos aún no implementados.
Datos de prueba siempre sintéticos, sin dominios/códigos académicos reales inventados.

## Matriz de pruebas futuras

| Área / requisito | Casos y resultado esperado | Nivel / hito |
|---|---|---|
| Migraciones | Crear BD vacía, aplicar migraciones y reiniciar; FK y UNIQUE reales rechazan duplicados; probar estrategia de reversión sobre BD desechable autorizada | MySQL integración / H02 |
| Mallas versionadas | Una materia en dos versiones con requisitos/semestres diferentes; sin contaminación entre versiones; rechazo de arista ajena, autorreferencia y ciclo indirecto; publicación inmutable | Unidad + MySQL / H03 |
| Perfil | Tres estados exactos; ausencia distinguida de no cursada; revisión histórica intacta; estado de otra malla rechazado; conflicto de revisión no sobrescribe | Unidad + integración / H04, D03/D11 |
| Prerrequisitos | Todos aprobados habilitan; uno reprobado/no cursado/ausente bloquea y explica causa; aprobada no seleccionable; semestre mayor no bloquea; sin requisitos habilita con reprobada/no cursada explícita; candidata sin declaración bloqueada | Unidad / H04 |
| Reglas no aportadas | No inferir aprobación de ancestros ni equivalencias; OR/correquisitos no admitidos sin diseño aprobado | Unidad / H03–H04 |
| Prioridades | 3+4 válido, 4+0 inválido, 2+5 inválido, 0+4 válido, 3+5 inválido; duplicados y categoría desconocida rechazados | Unidad + API / H06 |
| Mínimo | Envío vacío rechazado; una media o una baja basta, sin altas obligatorias (D02); guardar borrador vacío permitido; estudiante sin elegibles recibe explicación sin inventar excepciones | Unidad + API / H06 |
| Malla sin oferta (D05) | Toda pendiente de la malla con estado conocido y prerrequisitos aprobados es seleccionable; sin catálogo ni filtro de oferta por período; reporte advierte interés potencial y disponibilidad no confirmada | Unidad + API / H04, H10 |
| OTP | Correo permitido/prohibido, sufijo engañoso, normalización y cuentas inexistentes; respuestas genéricas; vencimiento, código incorrecto, reenvío invalida anterior, límite intentos y emisión compartido | Unidad + integración / H05 |
| Concurrencia OTP | Dos verificaciones simultáneas: solo una consume y crea sesión; reenvío concurrente no deja dos desafíos utilizables | MySQL integración / H05 |
| Sesión / rol | Caducidad, revocación, cookie, CSRF/origen, suspensión; registro no crea admin; estudiante no accede a reportes ni datos ajenos; cuerpo no puede elevar rol | API / H05, H06, H10 |
| Ciclo de solicitud | Borrador → envío → edición → actualización → retiro → recuperación → envío; revisiones/eventos conservados, una principal; guardar edición preserva envío previo | Integración / H06 |
| Captura | Antes de apertura, instante de apertura, justo antes del cierre y cierre exacto; semestre destino y ventana anterior configurable; UTC y zona IANA válida; límites [apertura, cierre) propuestos pendientes de revisión técnica; borrador no enviado automáticamente; sin cambios estudiantiles tras cierre | Reloj controlado + API / H06 |
| Cambios académicos | Incompatibilidad invalida y excluye toda la solicitud, sin contar materias restantes, en la misma transacción D04; cambio compatible actualiza fundamento; cambio posterior de carrera/malla rechazado según restricción propuesta mientras D11 siga pendiente; posteriores al cierre no alteran instantánea | Integración / H07 |
| Carreras concurrentes | Dos creaciones producen una principal; dos ediciones obsoletas no se pisan; envío y cambio de historial serializados; envío/retiro simultáneos dejan un estado coherente | MySQL integración / H06–H07 |
| Fallo transaccional | Error entre revisión, evento y puntero revierte todo; no queda vigente incompatible ni historial parcial | Integración con fallo controlado / H06–H07 |
| Conteos | Dos estudiantes con varias versiones; solo vigente cuenta una vez por materia/período; retiro/invalidación excluidos; misma materia en otro período separada | Integración / H10 |
| Dimensiones | Totales por prioridad suman total por materia; participantes distintos no son selecciones; semestre/malla/repetición provienen de revisión de envío; sin denominador institucional | Integración / H10 |
| CSV | Coincide con reporte y filtros en misma instantánea; UTF-8, comillas, saltos y fórmulas neutralizados; sin correos ni nombres estudiantiles; acceso no autorizado rechazado | Integración / H10 |
| Flujo local | OTP Mailpit → perfil → malla → borrador → envío → edición/retiro → reporte; persistencia tras reinicio sin limpiar volúmenes; sin SMTP externo | Integral / H11 |

«Carreras concurrentes» en la tabla refiere a condiciones de carrera entre operaciones,
no a cursar dos programas. La capacidad por asignatura no se prueba ni simula hasta
contar con fuente confiable y aprobación de alcance.

## Herramientas y evidencia esperadas

pytest para reglas/API/integración, Ruff para Python, herramientas del proyecto
Angular que se elijan en H01 para compilación y pruebas de interfaz; MySQL real
local de prueba para transacciones, FK, collation y bloqueos. Mailpit para recepción
local. Acordar herramientas y versiones sin instalar nada en fase 0.

Cada hito registrará comando exacto, código de salida, resultado y limitaciones;
si un servicio falta, reportar prueba no ejecutada. No presentar pruebas unitarias
como evidencia de integración MySQL. Probar regresión de invariantes al cambiar
solicitudes o conteos, sin repetir suites sin motivo.

## Verificación documental de fase 0

Revisar diff y espacios en blanco; comprobar que solo docs/ cambió, existen los
entregables, los enlaces locales apuntan a archivos existentes y los identificadores
D01–D13 usados corresponden a la tabla de decisiones. Lectura manual cruzada de
estados, tablas y API. No se ha validado renderizado Mermaid ni un contrato OpenAPI
formal: el diagrama y contratos son propuestas de texto, sin generación de código.


## Casos adicionales de esta revisión (futuros, no ejecutados)

- Integridad curricular / H03–H06: FK rechaza malla_asignatura inexistente; servicio
  rechaza entrada existente de otra malla al guardar y enviar, incluso si representa
  la misma asignatura de catálogo. Dos detalles iguales fallan; otra versión de
  malla no modifica selecciones existentes.
- Coexistencia / H06–H07: enviar A, guardar B vacío o académicamente incompatible,
  comprobar que A sigue contando y estado sigue enviada. Envío fallido de B conserva
  ambos punteros; envío válido reemplaza A y limpia trabajo. Retiro y recuperación
  conservan/copían trabajo según modelo sin envío automático. Rechazar matriz de
  punteros inválida, punteros iguales y referencias a otra principal.
- D04 con trabajo pendiente: historial invalida A aunque B sea válido; excluir toda
  A inmediatamente y conservar B sin contar. Si solo B queda incompatible, A sigue
  contando. Cambio compatible renueva fundamento de A sin perder B; enviar B exige
  revalidación contra perfil actual. Probar rollback y concurrencia con envío.
- Prioridades / H06: 1+6, 0+5 y 2+5 rechazados; 3+4, 0+4, una alta, una media y
  una baja aceptadas si elegibles; medias y bajas comparten límite cuatro. Aplicar
  máximos también a borradores y actualizaciones; vacío solo admitido en borrador.
- Historia curricular / H03, H10: cerrar período, cambiar nombre de catálogo y
  publicar nueva malla con otros nombres, semestre y requisitos. Repetir reporte y
  CSV con iguales filtros: mismas etiquetas, dimensiones y cantidades históricas.
  Publicación original permanece inmutable y referencias no se borran ni reasignan.
- Perfil / H04: una malla activa, revisiones antiguas consultables; publicar una
  malla no migra perfil. Cambio posterior de carrera/malla rechazado bajo la
  restricción recomendada; no equivalencias ni traslado automático de aprobaciones.

## Consolidación: casos de aceptación adicionales (futuros)

- H05: OTP válido de cuenta nueva crea solo estudiante y sesión; cuenta existente
  mantiene identidad/roles; suspensión impide acceso. Dos desafíos válidos para el
  mismo correo no duplican usuario. Alta de admin solo por procedimiento controlado
  auditado; ningún cuerpo público asigna roles. Fallo revierte consumo/alta/sesión.
- H06: pérdida de respuesta después de commit y reintento con igual clave/cuerpo
  recuperan exactamente el éxito original, incluso con revisión ya obsoleta; un
  evento y una versión enviada. Dos reintentos concurrentes producen un solo éxito
  persistido. Misma clave/cuerpo distinto devuelve 409; nueva clave/revisión obsoleta
  devuelve 409. Sin clave devuelve 422. Fallo antes de commit no deja registro ni
  efectos; reintento aplica reglas actuales. Reintento tras retiro, invalidación o
  cierre no restaura vigencia y GET muestra estado actual. Claves aisladas por dueño/período.
- H06: publicación exige inicio_periodo y orden desde < hasta < inicio; destino
  pasado o igual al reloj se rechaza. Zona inválida, hora sin desplazamiento y
  desplazamiento incompatible se rechazan; fixture sintético cruza cambio de fecha
  entre zona local y UTC. Publicación congela configuración; captura [desde, hasta).
- H07: un perfil con solicitudes de un período abierto y otro cerrado cambia su
  historial: solo la abierta se revalida/invalida o renueva, la cerrada conserva
  revisión, punteros, etiquetas y conteos. Probar carrera con cierre bajo bloqueo.
- H10: mismo nombre/código en dos identidades no fusiona materias; misma identidad
  en dos mallas con semestre/prerrequisitos distintos conserva filas separadas por
  versión/entrada curricular en pantalla y CSV. Reprobada implica repetición
  declarada, no_cursada no; desconocido impide envío. Prioridades y semestres se
  toman del fundamento del envío; no recalcular con perfil actual.
