# PREVIA — Requisitos funcionales iniciales (v0.6, D01–D06 confirmadas)

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

## 1. Objetivo
Aplicación web para recopilar **al final del semestre**, antes de planificar el siguiente período, la intención de cursar materias y sus prioridades. Provee agregados de demanda para apoyar a coordinación/Registro Académico. Es una señal de interés, no una predicción certificada de elegibilidad ni una matrícula oficial.

## 2. Límites de la versión 1
- Se ejecuta localmente y desde cero.
- No conecta con sistemas académicos oficiales, no usa credenciales oficiales de matrícula, no reserva cupos ni asigna paralelo, hora o aula.
- No habrá etapa de reconfirmación en v1. Puede considerarse en una versión futura.
- No se calcula tasa de participación institucional sin padrón oficial; comparaciones históricas de participantes son futuras.
- Durante el desarrollo se emplearán cuentas de prueba, malla pública cuando se suministre y datos sintéticos claramente identificados.

## 3. Actores
- **Estudiante**: verifica control de un correo autorizado, completa su perfil académico, declara estados por materia, revisa malla, selecciona cursos, asigna prioridad y gestiona su intención durante el plazo de captura.
- **Administrador o personal autorizado**: configura catálogo/malla, períodos y fechas; accede a reportes agregados y exportaciones. Los permisos de administración no se obtienen mediante autoregistro.

## 4. Autenticación
- Registro/acceso por correo institucional permitido y código de un solo uso (OTP); sin contraseña estudiantil ni Google OAuth. La verificación exitosa inicia sesión en la cuenta existente o crea una cuenta de estudiante en el primer acceso. El alta de administradores se realiza exclusivamente mediante procedimiento controlado, nunca por registro público.
- Código temporal y de uso único; limitar intentos, emisión y reenvíos; no revelar si una cuenta existe; sesión segura. Valores como duración exacta son configurables.
- Verificar el buzón **no certifica** condición de estudiante activo; esta limitación debe aparecer en la documentación y reportes.
- Para desarrollo local se puede usar Mailpit o un servidor de correo simulado. Correo real necesita servicio SMTP autorizado.

## 5. Perfil y malla
- Carrera, versión de malla (cuando proceda) y semestre actual declarado (para fines analíticos, no bloqueo automático).
- Por cada asignatura del historial declarado se distinguen exactamente tres estados académicos de cara al estudiante: **aprobada, reprobada, no cursada**.
- La ausencia de declaración es información desconocida, no un cuarto estado académico; nunca equivale automáticamente a aprobada ni a no cursada. Se exige estado conocido de la candidata y aprobación declarada de todos sus prerrequisitos (D03).
- No confundir 'cursada' con 'aprobada'. La interfaz debe evitar afirmar resultados desconocidos.
- La malla define materias, identificadores, semestre curricular y prerrequisitos. Correquisitos y reglas especiales necesitan respaldo documental antes de implementarse.
- No se puede elegir una materia ya aprobada.
- Puede elegirse materia reprobada o no cursada si todos los prerrequisitos configurados figuran aprobados.
- Materias con prerrequisitos sin cumplir están **bloqueadas** y muestran la causa, también con validación del servidor.
- No se impone restricción por semestre curricular cuando los prerrequisitos están cumplidos.

## 6. Intenciones y prioridades
- Una solicitud principal por estudiante y período académico; la relación estudiante/asignatura/período no debe duplicar la demanda.
- Categorías: **alta**, **media** y **baja**.
- Límite: hasta **3** materias altas y hasta **4** adicionales medias/bajas; máximo **7** asignaturas en total.
- Para enviar se requiere al menos una asignatura de cualquier prioridad. Las altas son opcionales; se admite un envío compuesto solo por medias/bajas, hasta cuatro (D02).
- Borradores no cuentan; solo una versión enviada y vigente cuenta para demanda. Retirada no cuenta.
- El estudiante puede editar durante el plazo abierto sin un límite arbitrario de tres ediciones; preservar el historial de cambios.
- Puede retirar y recuperar la intención durante el plazo abierto, con nueva versión y sin segunda solicitud principal.
- Al cerrar la captura, se bloquea la edición y no se envían automáticamente los borradores.
- Si un cambio del historial académico vuelve incompatible una solicitud enviada durante la captura, toda esa solicitud deja de contar inmediatamente. El cambio y la exclusión son transaccionales; se conserva el historial y se exige corregir y enviar nuevamente. No se eliminan solo las materias incompatibles para seguir contando el resto (D04).
- Tras el cierre se conserva la instantánea histórica del período; cambios posteriores del historial no alteran su demanda (D04).

## 7. Reportes
- Demanda por asignatura, período y prioridad; un estudiante cuenta a lo sumo una vez por asignatura en el período.
- Analizar demanda por semestre curricular, semestre declarado del estudiante y posible repetición.
- Posible comparación con capacidad de referencia solo si se dispone de datos confiables.
- Separar 'demanda declarada con prerrequisitos según autodeclaración' de 'elegibilidad oficial' (no disponible).
- Exportación inicial a CSV.

## 8. Criterio de éxito de la versión local
En una ejecución local reproducible, un estudiante de prueba puede verificar correo, configurar perfil, elegir únicamente materias habilitadas por las reglas de malla, asignar prioridades, guardar/enviar/editar/retirar en plazo; la información persiste al reiniciar; personal autorizado puede consultar y exportar reportes con conteos correctos y permisos efectivos.

## 9. Malla, período y captura confirmados

- Puede seleccionarse cualquier asignatura pendiente de la malla correspondiente (reprobada o no cursada), con estado conocido y todos los prerrequisitos declarados aprobados. No existe catálogo independiente de oferta por período en v1 (D03/D05).
- Los reportes representan interés potencial, no disponibilidad confirmada (D05).
- El período identifica el semestre de destino; la captura ocurre en una ventana anterior con fechas configurables. Se almacenan instantes en UTC y se configura una zona horaria IANA. No hay reaperturas excepcionales en v1 (D06).

## Estatus de planificación

D01–D06 están **confirmadas** en [decisions.md](decisions.md).
D07–D13 distinguen recomendaciones listas para desarrollo local y pendientes institucionales en [planning-review.md](planning-review.md).
La aprobación funcional no aprueba automáticamente mecanismos técnicos ni autoriza implementación.
