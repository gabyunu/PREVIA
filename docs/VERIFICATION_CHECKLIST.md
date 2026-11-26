# Final-term evaluation checklist (run on Windows 11 before submission)

- [ ] Docker Desktop + WSL 2 started, `docker compose ps` shows MySQL and Mailpit.
- [ ] `scripts/windows-setup.ps1` finished successfully.
- [ ] Flask endpoint `/health` returns `{ "status": "ok" }`.
- [ ] `/openapi.json` displays all documented endpoints; Swagger `/docs` works when online.
- [ ] Angular `npm.cmd run build` passes.
- [ ] `scripts/windows-tests.ps1` passes Flask SQLite tests.
- [ ] Create admin user with OTP and grant role using `app.db.admin_access`.
- [ ] Admin GUI creates a planning record in MySQL.
- [ ] Admin GUI displays the newly created record (Read).
- [ ] Admin GUI updates planned capacity (Update).
- [ ] Admin GUI deletes unreferenced planning record (Delete).
- [ ] Unauthorized students get 403 on admin CRUD and writes without CSRF are rejected.
- [ ] Student profile and prerequisite eligibility work against actual MySQL.
- [ ] Saving, submitting, and viewing history persists across reloads.
- [ ] DBeaver displays the ER relationships and read-only SQL output.
- [ ] Report from persistent student submissions differs from synthetic demonstration.
- [ ] Exported `database/schema_mysql.sql` is provided, but not applied on top of migrations.
- [ ] README/docs and GitHub branch contain the changes; actual `git push` completed.
- [ ] Both presenters rehearse 15 minutes and prepare an offline screenshot fallback.

Known unverifiable locally while authoring: the new Flask stack and Windows GUI could not be executed in the current offline environment. Do not check those boxes without running them.


## H08 - Portales estudiante / administrador

- [ ] Ejecutar `scripts\windows-demo-accounts.ps1` sobre MySQL existente.
- [ ] Estudiante: entrar con `estudiante.demo@estudiantes.example.test` y OTP de Mailpit; verificar que solo se vean Inicio, Perfil, Habilitadas, Selección e Historial.
- [ ] Estudiante: URL `/demanda` y `/planificacion` redirigen al espacio estudiantil; API `/api/v1/admin/*` responde 403.
- [ ] Administrador: entrar con `admin.demo@estudiantes.example.test` y OTP de Mailpit; verificar Panel general, Demanda y Planificación CRUD.
- [ ] Administrador: URL `/mi-perfil-academico` redirige al panel; API `/api/v1/me/*` responde 403.
- [ ] Sin sesión, las dos familias de rutas protegidas responden 401.
- [ ] Crear, consultar, actualizar y eliminar un registro de planificación; confirmar su persistencia en MySQL con DBeaver.
- [ ] Comprobar que no se borran versiones de solicitudes históricas.
- [ ] Ejecutar `scripts\windows-role-tests.ps1`; anotar salida y número de pruebas aprobadas.

**No marcar comprobaciones como aprobadas sin ejecutarlas en la laptop de Windows 11.**
