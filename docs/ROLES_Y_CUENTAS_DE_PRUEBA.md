# PREVIA — Portales separados y cuentas de prueba (Windows 11)

## Objetivo

Esta versión distingue dos roles **mutuamente excluyentes**. Se conservan la malla piloto y la base `previa_dev` que se crearon anteriormente.

| Rol | Correo de prueba | Pantallas | Rutas de API |
| --- | --- | --- | --- |
| Estudiante | `estudiante.demo@estudiantes.example.test` | Inicio, Mi perfil académico, Habilitadas, Mi selección, Historial | `/api/v1/me/*` |
| Administrador | `admin.demo@estudiantes.example.test` | Panel general, Demanda, Planificación (CRUD) | `/api/v1/admin/*` |

**No existen contraseñas fijas.** PREVIA usa códigos temporales de ocho dígitos enviados a **Mailpit** (`http://127.0.0.1:8025`) cada vez que se inicia sesión. No se muestra ni se expone un código OTP estático en la interfaz ni en el repositorio.

La cuenta administrativa solo se crea mediante un comando local explícito, no mediante el registro público. Un correo ficticio por sí solo no concede el rol de administración. El comando es idempotente, no convierte cuentas con perfil estudiantil en administradores y se detiene ante roles preexistentes incompatibles.

## Actualización de una instalación existente de Windows 11

Si ya instalaste la versión anterior y la base MySQL contiene datos, **no borres el volumen de Docker ni el archivo `.env`**.

1. Detén Angular y Flask con `Ctrl+C` en sus terminales.
2. Extrae el ZIP de actualización (`PREVIA_Actualizacion_Roles_Windows11.zip`) **sobre la raíz existente del proyecto** (carpeta que contiene `compose.yaml`, `backend`, `frontend` y `scripts`).
3. Desde PowerShell dentro del proyecto, ejecuta:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\windows-demo-accounts.ps1
```

4. En dos terminales distintas, inicia:

```powershell
.\scripts\windows-start-api.ps1
```

```powershell
.\scripts\windows-start-frontend.ps1
```

5. Abre `http://127.0.0.1:4200` y elige el portal. La dirección del correo aparece en el formulario y puedes copiarla con el botón «Usar este correo».
6. Haz clic en «Solicitar código de acceso», abre Mailpit y usa el código **más reciente** para ese correo.

Si todavía no existe el entorno, la ejecución inicial de `windows-setup.ps1` ahora crea ambas cuentas de prueba al final de las migraciones, sin contraseñas permanentes.

**No ejecutes** `docker compose down -v`, `DROP DATABASE`, ni vuelvas a crear el archivo `.env`. Eso pondría en peligro tu base de desarrollo y las sesiones existentes.

## Seguridad: no basta con ocultar la navegación

- `role-guards.ts` deniega la navegación Angular a rutas que no corresponden al rol.
- `flask_api.py` verifica **en el servidor** cada petición a `/api/v1/admin/*` y `/api/v1/me/*` mediante una sesión real y las relaciones `usuario`, `rol` y `usuario_rol` de MySQL. 
- Una cuenta con ambos roles se rechaza en los espacios protegidos; se espera un único rol.
- La API de planificación conserva controles de CSRF/origen y las validaciones de campos.
- Los estudiantes **no pueden** consultar los indicadores globales de demanda ni editar cupos planificados, incluso llamando al endpoint manualmente.
- Los administradores **no pueden** entrar a las rutas de perfil, selección o historial estudiantil.
- Las estadísticas son intenciones de cursar materias; **no son matrículas confirmadas ni reservas de plazas**.

## Pruebas para la evaluación

```powershell
.\scripts\windows-tests.ps1
```

Con los servidores iniciados verifica también:

1. Entra como estudiante; debe haber cinco pestañas académicas y **ninguna** administrativa.
2. Intenta abrir `/demanda` y `/planificacion` mientras eres estudiante: debe redirigirse al espacio estudiantil.
3. Cierra sesión; entra como administrador y revisa Panel general, Demanda y Planificación.
4. Desde Planificación crea un registro de cupos orientativos, consulta su valor, modifícalo y elimínalo; comprueba el resultado en DBeaver.
5. Intenta abrir `/mi-perfil-academico` como administrador: debe redirigirse al panel.
6. Confirma en las pruebas HTTP que el backend devuelve `403` para solicitudes de un rol que no tiene permiso, y `401` sin sesión.

Para mostrar datos en el panel, primero debe haber **solicitudes enviadas de verdad a la API en MySQL**. El hecho de contar con 3.000 registros sintéticos para otra demostración no llena automáticamente el informe administrativo.

## Advertencias para la entrega

Esta adaptación requiere ejecutar las pruebas en la laptop Windows 11 para confirmar su comportamiento extremo a extremo. No se deben confundir la compilación frontend o la creación de usuarios con pruebas integrales aprobadas. Nunca publiques `.env`, cookies, contraseñas MySQL ni OTP vigentes.
