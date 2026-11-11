# PREVIA — Requisitos funcionales iniciales (v0.5, borrador de trabajo)

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
- Registro/acceso por correo institucional permitido y código de un solo uso (OTP); sin contraseña estudiantil ni Google OAuth.
- Código temporal y de uso único; limitar intentos, emisión y reenvíos; no revelar si una cuenta existe; sesión segura. Valores como duración exacta son configurables.
- Verificar el buzón **no certifica** condición de estudiante activo; esta limitación debe aparecer en la documentación y reportes.
- Para desarrollo local se puede usar Mailpit o un servidor de correo simulado. Correo real necesita servicio SMTP autorizado.

## 5. Perfil y malla
- Carrera, versión de malla (cuando proceda) y semestre actual declarado (para fines analíticos, no bloqueo automático).
- Por cada asignatura del historial declarado se distinguen exactamente tres estados académicos de cara al estudiante: **aprobada, reprobada, no cursada**.
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
- Materias adicionales son opcionales. El mínimo exacto para el envío está **pendiente** (se propuso una alta; debe aprobarse explícitamente).
- Borradores no cuentan; solo una versión enviada y vigente cuenta para demanda. Retirada no cuenta.
- El estudiante puede editar durante el plazo abierto sin un límite arbitrario de tres ediciones; preservar el historial de cambios.
- Puede retirar y recuperar la intención durante el plazo abierto, con nueva versión y sin segunda solicitud principal.
- Al cerrar la captura, se bloquea la edición y no se envían automáticamente los borradores.
- Si cambia el historial declarado y se vuelven inválidas las materias enviadas, el servidor debe impedir reportar una intención incompatible como válida; especificar el mecanismo exacto antes de implementarlo.

## 7. Reportes
- Demanda por asignatura, período y prioridad; un estudiante cuenta a lo sumo una vez por asignatura en el período.
- Analizar demanda por semestre curricular, semestre declarado del estudiante y posible repetición.
- Posible comparación con capacidad de referencia solo si se dispone de datos confiables.
- Separar 'demanda declarada con prerrequisitos según autodeclaración' de 'elegibilidad oficial' (no disponible).
- Exportación inicial a CSV.

## 8. Criterio de éxito de la versión local
En una ejecución local reproducible, un estudiante de prueba puede verificar correo, configurar perfil, elegir únicamente materias habilitadas por las reglas de malla, asignar prioridades, guardar/enviar/editar/retirar en plazo; la información persiste al reiniciar; personal autorizado puede consultar y exportar reportes con conteos correctos y permisos efectivos.
