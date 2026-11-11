# PREVIA — Registro de decisiones (v0.5)

## Confirmado por el alcance acordado
- Se desarrolla una versión nueva **desde cero**.
- Se usará al cierre del semestre para declarar interés de materias para el siguiente período.
- Es un sistema de retroalimentación para planificación, no una continuación del trámite de matrícula oficial.
- Ejecución local en v1.
- Angular, FastAPI, SQLAlchemy, MySQL y Docker como tecnologías previstas.
- Estados académicos declarados que verá el estudiante: aprobada, reprobada, no cursada.
- La malla debe ser visible e incluir relaciones de prerrequisitos.
- Se bloqueará la selección de asignaturas sin prerrequisitos declarados cumplidos.
- Hasta tres asignaturas altas y cuatro adicionales medias/bajas.
- La reconfirmación no estará en v1 por falta de tiempo; reconsiderable en el futuro.
- Se inicia sesión mediante control de correo de dominio institucional y OTP, sin integración con Google OAuth ni el sistema oficial.
- No se calcula participación de toda la institución sin padrón; eventual análisis entre períodos posteriores.

## Recomendado en la planificación (debe consolidarse en revisión)
- Borradores no cuentan en demanda; no existe envío automático.
- Editar y retirar antes del cierre, conservando historial y una única solicitud principal por estudiante y período.
- Un rol administrador preasignado gestiona catálogo, períodos y reportes.
- Mailpit para probar recepción de códigos en local; envío real pendiente de proveedor.
- CSV para primera exportación.

## Puntos por resolver antes de implementar funcionalidades afectadas
1. **Dominio(s) institucional(es)** permitidos, y reglas para distintos tipos de cuentas del mismo dominio.
2. **Malla real**, carrera objetivo, versión de malla, asignaturas, prerrequisitos y reglas especiales (correquisitos, créditos, excepciones).
3. **Mínimo para enviar**: ¿al menos una materia alta o basta una materia de cualquier prioridad? ¿Cómo manejar egresandos sin materias elegibles?
4. **Perfil declarado**: ¿cómo completar estados sin obligar a marcar manualmente toda la malla? ¿Qué pasa si faltan calificaciones al final de semestre?
5. **Actualización posterior al envío**: tratamiento exacto de materias que dejan de ser elegibles al editar el historial y de cambios de malla/período.
6. **Ventana de captura**: fechas, zona horaria, apertura/cierre y reglas de excepciones administrativas.
7. **Oferta vs. malla**: si cualquier asignatura pendiente de malla es seleccionable o solo las previstas para el siguiente período.
8. **Acceso administrativo**: quién administra, forma de crear el primer administrador y política de acceso sin credenciales institucionales.
9. **Alcance de datos personales y retención**: consentimiento/aviso, datos mínimos, acceso, borrado y protección.

## No afirmar
- Que la verificación por correo certifica matrícula activa.
- Que la información declarada permite elegibilidad oficial.
- Que se conoce la demanda de toda la institución.
- Que existen fechas, mallas o datos académicos oficiales autorizados si no se han proporcionado.
