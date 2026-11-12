# PREVIA — Arquitectura y comportamiento propuestos

## Alcance vigente H07 — Historial real

**Confirmado y autorizado:** consulta propia autenticada del historial MySQL por
período, con paginación de solicitudes y versiones, detalle de prioridades,
semestres, fechas, eventos y vigencia. Reutiliza tablas e instantáneas H05; no
modifica OTP, prerrequisitos, Demanda, envío ni vigencia. Sin retiro ni
reconfirmación. Véase [contrato y evidencia H07](h07-history.md).
La denominación H07 de esta entrega sustituye solo la numeración del plan antiguo
que llamaba H07 a revalidación; no autoriza otro alcance.
**Recomendado y adoptado:** lectura de 10 registros por página (máximo API 50),
creación de principal inferida de su primera versión existente.
**Pendiente:** políticas institucionales y revisión visual manual en Firefox.


## Alcance vigente H06

**Confirmado y autorizado:** Demanda y CSV administrativos desde solicitudes
persistidas enviadas y vigentes; separación por período/malla, cupos NULL/cero y
fixture H01-C independiente. Alta administrativa local explícita y auditada, sin
promoción pública ni cambios a OTP o D03/D04. Sustituye las restricciones históricas
sobre reportes pendientes solo para este alcance. Contrato, límites, verificaciones
y guía Firefox en [h06-demand.md](h06-demand.md). Políticas institucionales y
recorrido visual manual siguen **pendientes**.

## Alcance vigente H05-B

**Confirmado y autorizado:** envío definitivo propio, consulta y correcciones
durante captura conforme a D01/D04; versiones y fundamento históricos conservados.
Idempotencia transaccional adoptada para el piloto. Véase
[h05-b-submit.md](h05-b-submit.md). Sustituye las restricciones históricas de
H05-A para este alcance; reportes, retiro/recuperación y políticas institucionales
siguen pendientes.

## Alcance vigente H05-A

**Confirmado y autorizado:** selección y borrador propio persistido, sin envío ni
reportes reales. Esta ampliación sustituye las restricciones históricas solo para
H05-A. Contratos, mecanismos adoptados, evidencia y pendientes en
[h05-a-drafts.md](h05-a-drafts.md). D03 y límites independientes se conservan.

## Alcance vigente H04-B y ratificación D03

**Confirmado:** consulta de elegibilidad curricular autodeclarada y provisional
con la última revisión propia. APROBADA no es seleccionable; REPROBADA y
NO CURSADA requieren todos los prerrequisitos APROBADA y reglas suficientemente
verificadas. Una candidata sin declaración permanece bloqueada aunque cumpla
los prerrequisitos. «Prerrequisitos cumplidos» y «habilitada para selección»
son resultados distintos. Véase [contrato y evidencia H04-B](h04-b-eligibility.md).
Este alcance sustituye las menciones históricas a elegibilidad pendiente.
Solicitudes, cambios de malla y certificación institucional siguen fuera de alcance.


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

## Estatus y dependencias

**Confirmado**: Angular + TypeScript; FastAPI + Pydantic + SQLAlchemy; MySQL;
Docker Compose local; pytest y Ruff; backend responsable de permisos y reglas.
No implementar en fase 0. **Recomendado**: el diseño siguiente, Alembic para
migraciones y Mailpit para correo local. **Confirmado funcionalmente**: D01–D06. **Recomendado/Pendiente**: configuración local y datos institucionales distinguidos
en planning-review.md (D07–D13). Esquema detallado en data-model.md, contratos en api-design.md.

Flujo: Angular → API HTTP → servicios de dominio → persistencia → MySQL.
Servicios separados para identidad, catálogo, perfil/elegibilidad, solicitudes y
reportes. La API valida estructura con Pydantic; dominio valida reglas y permisos;
MySQL refuerza integridad. No exponer acceso directo a tablas desde Angular.

## Evaluación de prerrequisitos

Para cada candidata, cargar la malla de la revisión de perfil, su estado declarado
y todos los requisitos directos. Debe pertenecer a la malla, tener declaración
conocida (D03), no estar aprobada y tener todos los requisitos configurados
aprobados. Reprobada/no cursada son elegibles si cumplen lo anterior. Sin requisitos,
la conjunción vacía se cumple; no se compara semestre declarado con curricular.
D05 permite cualquier pendiente de esa malla; no se valida oferta independiente en v1.

Mostrar causas estructuradas: aprobada, falta_declaracion, prerrequisito_pendiente,
fuera_de_malla. No inferir aprobación por haber
aprobado otra materia posterior. Los requisitos son directos y conjuntivos;
validar el grafo completo al publicar. Exigir ancestros además de requisitos
configurados sería otra regla académica, no una inferencia automática.

Guardar borrador puede conservar selecciones ahora inválidas con advertencias,
pero exige pertenencia a la malla de la revisión, colección sin duplicados, prioridades válidas y máximos 3+4. Enviar o
actualizar exige todas las validaciones sobre el servidor en la misma transacción.
Los límites son independientes: 2 altas no permiten 5 adicionales; 3 altas y 4
adicionales sí. El envío requiere al menos una materia de cualquier prioridad; ninguna alta es obligatoria (D02). Nunca sustituir un rechazo por eliminar
materias silenciosamente. La respuesta describe autodeclaración, no elegibilidad oficial.

## Máquina de estados propuesta para reglas confirmadas D01, D04, D06

Estado de la solicitud principal: borrador, enviada, retirada o invalidada.
«Invalidada» es estado interno propuesto que se explica como «requiere revisión»;
no es un cuarto estado académico. Cierre pertenece al período, no a una versión.
Estado efectivo combina solicitud y ventana: al cerrar no se convierte borrador
en enviada ni se modifica una enviada; toda mutación estudiantil queda bloqueada.

| Origen | Acción en captura abierta | Resultado | Cuenta en demanda |
|---|---|---|---|
| No existe | Guardar | Principal única, revisión de trabajo, borrador | No |
| Borrador | Guardar | Nueva revisión de trabajo | No |
| Borrador | Enviar válido | Enviada, puntero vigente a revisión enviada | Sí |
| Enviada | Guardar edición | Nueva revisión de trabajo; vigente anterior se conserva | Sí, anterior |
| Enviada | Enviar actualización válida | Reemplazar puntero vigente atómicamente | Sí, nueva |
| Enviada | Retirar | Retirada, quitar puntero vigente, evento conservado | No |
| Retirada/invalidada | Recuperar | Nueva revisión de trabajo como borrador; validación para reenviar | No |
| Enviada | Cambio incompatible de perfil | Invalidada, quitar vigente y conservar contenido/evento | No |
| Cualquiera | Cierre de captura | Estado preservado, comandos estudiantiles rechazados | Solo enviada vigente |

Recuperar no envía automáticamente. Retirar repetidamente puede devolver el estado
actual sin generar otra revisión. No limitar cantidad de ediciones. Reintentar envío con la misma clave y cuerpo recupera el éxito original sin duplicar
eventos ni demanda (contrato de idempotencia en api-design.md). Conservar versiones y
transiciones permite distinguir guardar, actualizar y retirar sin otra principal.

## Consistencia y cambios académicos

En escrituras de solicitudes: autenticar, autorizar dueño/rol, bloquear perfil_estudiante,
período y solicitud en ese orden, comprobar ventana con reloj del servidor,
consultar primero la clave idempotente en submit (si existe, resolver según API);
para una operación nueva comparar revision_control esperada, validar colección y revisión de perfil actual,
insertar revisión/evento y cambiar punteros, confirmar todo junto. Orden uniforme
de bloqueos para evitar interbloqueos; reintentos internos acotados sin duplicar
efectos. UNIQUE resuelve carrera de creación inicial; recuperar conflicto con
respuesta 409. Reporte lee una instantánea consistente en una transacción.

D04 confirmado: el cambio de historial obtiene el mismo bloqueo de estudiante,
revalida todas sus solicitudes vigentes en períodos abiertos y, si invalida alguna,
quita la vigencia de toda la solicitud en la misma transacción, sin contar un subconjunto restante. La interfaz anticipa consecuencias;
respuesta enumera solicitudes afectadas. Si se rechaza la operación, no hay
cambios parciales. Si la intención sigue válida, crear revisión equivalente con
el nuevo fundamento académico y evento, conservando las anteriores. Esto actualiza
correctamente dimensiones como semestre declarado o posible repetición.

La ventana bloquea mutaciones de solicitudes del período, no cambios posteriores
del historial del perfil: estos conservan intactas las solicitudes cerradas.
D06 confirma período destino, captura anterior configurable, instantes UTC y zona
IANA configurable. Se propone intervalo [apertura, cierre); la propuesta consolidada de validación de fechas y horas se detalla en
data-model.md y api-design.md, sin convertirla en calendario institucional.

Después del cierre, congelar solicitud y su revisión académica para el reporte;
perfil posterior solo afecta períodos futuros. Un cambio tardío no certifica ni
corrige retrospectivamente elegibilidad oficial. Una sola malla activa por perfil en v1. Mientras D11 siga pendiente, se recomienda
rechazar cambios de carrera/malla después de crear el perfil; no aplicarles
automáticamente la política de cambios del historial ni migrar aprobaciones. Publicaciones
de catálogo/malla inmutables evitan invalidación masiva silenciosa; correcciones
administrativas históricas quedan pendientes; reaperturas excepcionales están excluidas de v1 por D06.

## Identidad y seguridad propuestas (D08–D12)

1. Recibir correo, validar sintaxis y dominio exacto contra lista configurada;
   definir normalización antes de UNIQUE, sin asumir que toda parte local sea
   insensible a mayúsculas. No aceptar subdominios por coincidencia de sufijo.
2. Devolver respuesta genérica para solicitudes bien formadas, exista o no cuenta.
   Validar dominio en servidor y limitar también solicitudes que no envían correo.
   Usar desafío opaco y propósito acceso; no aceptar desafío de otro correo/propósito.
3. Generar código con fuente criptográfica. Propuesta revisable: 8 dígitos, 10
   minutos, 5 intentos, 60 segundos entre emisiones, máximo 5 emisiones por hora
   por correo y límites por IP adicionales configurables. No son valores aprobados.
   Persistir HMAC con clave fuera de BD para resistir búsqueda del espacio pequeño;
   comparar en tiempo constante. No registrar códigos ni secretos.
4. Invalidar desafío anterior al reenviar; contador de emisión por correo/IP
   persiste entre reenvíos. Expirar desafíos y bloquear tras máximo de intentos.
   Consumo y creación de sesión atómicos bajo bloqueo: código de uso único incluso
   con verificaciones concurrentes. Reintento o código viejo devuelve error genérico.
5. Verificación exitosa inicia sesión en el usuario existente o crea cuenta con rol
   estudiante e identidad de perfil sin datos curriculares si es primer acceso.
   Consumo, creación y sesión son atómicos; nunca crea ni promueve administradores. Verificar correo
   prueba control del buzón; no actividad académica. Suspensión de cuenta prevalece.
6. Sesión opaca aleatoria, digest en BD, revocable en logout; rotar al autenticar.
   Proponer duración absoluta 8 horas y caducidad por inactividad 30 minutos, por
   aprobar. Cookie HttpOnly, SameSite y Secure bajo HTTPS; excepción HTTP local
   explícita. No guardar tokens en localStorage. Protección CSRF en escrituras con
   cookie y validación de origen; CORS limitado al frontend local configurado.
7. Rol administrativo preasignado mediante procedimiento local autorizado y auditado,
   sin contraseña estudiantil y sin promoción por correo. Definir primer administrador
   antes de habilitar endpoints de catálogo/reportes. Estudiante solo accede a sus
   datos; reportes/CSV requieren administrador; ninguna API admite rol desde cliente.

Mailpit aislado en entorno local recibe solo cuentas sintéticas y permite probar
recepción sin SMTP externo. Limitar exposición del buzón de prueba a localhost;
no crear un atajo de autenticación que imprima OTP en logs o acepte código universal.
SMTP real, proveedor y credenciales requieren autorización posterior; nada externo
se invoca en fase 0. Secretos futuros fuera de Git, ejemplos ficticios en .env.example.

Retención de desafíos, sesiones, auditoría, perfiles e históricos requiere D10.
Evitar datos personales en logs y exportaciones; auditoría de operaciones privilegiadas
con actor, momento y referencia, no cuerpos completos. Controles de emisión deben
funcionar con varios procesos (almacenamiento compartido), no solo memoria local.

## Reportes: reglas confirmadas y diseño propuesto

La unidad es una selección de la versión vigente de una principal enviada del
período. Filtrar estado enviada y puntero vigente no nulo; unir exclusivamente esa
versión y sus detalles. Borradores, retiradas, invalidadas y versiones anteriores
quedan excluidos. UNIQUE de principal/detalle garantiza un estudiante por materia
por período; COUNT DISTINCT por estudiante puede reforzar la consulta, sin ocultar
fallos de integridad. No sumar versiones ni unir eventos antes de contar.

Agrupar por período/versión de malla/entrada curricular/prioridad y opcionalmente
semestre curricular, semestre declarado y repetición declarada (D13). Tomar dimensiones de la revisión
académica del envío vigente, nunca del perfil actual. Tras cierre, esas dimensiones
son estables. En grupos por malla un estudiante solo tiene una malla en esta propuesta.
Total de selecciones no equivale al total de estudiantes participantes; publicar
ambos con etiquetas distintas. Total por materia es suma de sus prioridades.

CSV inicial agregado, mismos filtros y consulta que pantalla, una instantánea por
exportación, período e instante de generación explícitos, sin correos ni nombres
estudiantiles. Neutralizar celdas de texto que hojas de cálculo interpreten como
fórmulas; escapar comillas/separadores y declarar codificación. Considerar divulgación
de grupos pequeños al aprobar D10. Advertencia visible: «Demanda declarada con
prerrequisitos según autodeclaración; no acredita elegibilidad oficial ni matrícula
activa ni disponibilidad confirmada; representa interés potencial». Capacidad y brecha solo con fuente confiable; sin tasas institucionales.


## Precisiones de integridad para revisión del modelo

Detalle referencia malla_asignatura; el servicio exige que pertenezca a la malla de
la revisión académica, incluso al guardar borrador. La FK garantiza existencia;
la igualdad curricular se valida transaccionalmente en backend.

La matriz de punteros de data-model.md es la autoridad propuesta: enviada requiere
vigente y permite trabajo distinto; guardar no cambia ese estado. Enviar válido
sustituye vigente y limpia trabajo atómicamente; un fallo conserva ambos. Retiro e
invalidación quitan vigente, conservando trabajo si existe. D04 evalúa el envío
vigente aunque el borrador difiera. Una renovación compatible del fundamento no
sobrescribe ni envía el trabajo pendiente. Nunca contar la versión de mayor número.

Para reportes históricos, seguir detalle → malla_asignatura publicada e inmutable,
con código/nombre publicados, semestre y prerrequisitos congelados; conservar también
etiquetas de carrera/versión. No usar nombres del catálogo mutable. Publicar otra
malla no migra perfiles ni cambia referencias históricas. Este mecanismo sigue
recomendado bajo D11; la conservación tras cierre es confirmada por D04.

## Precisiones de consolidación para desarrollo local

**Confirmado:** cambios del historial solo pueden invalidar solicitudes cuya
captura sigue abierta. Revalidación, renovación compatible y cambios de punteros
se limitan a esos períodos; nunca modificar una solicitud cerrada ni sus dimensiones.
Tomar períodos afectados en orden de ID y comprobar el reloj después del bloqueo;
si el cambio obtiene el bloqueo tras cierre, conservar la solicitud histórica.
El envío y el cambio de historial comparten bloqueo de estudiante.

**Recomendado:** adoptar `inicio_periodo` y validaciones de publicación descritas en
el modelo/API para demostrar que la captura precede al destino; la etiqueta del
período por sí sola no lo demuestra. Son reglas técnicas propuestas, sin fechas reales.

**Reportes v1, recomendado D13:** agrupar siempre por versión de malla y
malla_asignatura, además de período/prioridad; admitir desglose por semestre curricular,
semestre declarado y repetición declarada. Esta última es `reprobada` en la revisión
académica que fundamenta el envío; `no_cursada` no indica repetición. No inferir intentos.
Incluso si dos versiones comparten asignatura_id, conservar filas distintas, pues
semestre y requisitos pueden diferir. Códigos o nombres iguales no prueban identidad:
la importación solo comparte asignatura_id con identidad respaldada por fuente
autorizada; ante duda, mantener identidades separadas. No inferir equivalencias ni
sumar automáticamente entre mallas. Los participantes globales usan DISTINCT del
universo filtrado; nunca sumar subtotales de participantes. Pantalla y CSV siguen
las mismas claves y etiquetas históricas. Equivalencias y consolidación curricular
entre versiones quedan fuera de v1 sin decisión autorizada posterior.
