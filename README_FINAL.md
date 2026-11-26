# PREVIA — Windows 11 Final Term Project Package

An academic demand planning prototype with **Angular 22**, a **Flask REST server with Flask-SQLAlchemy**, and **MySQL 8.4**.

## Start here

1. Read [Windows 11 installation](docs/WINDOWS_11.md).
2. Extract the adapted ZIP (or merge changes into your Git clone after review).
3. In PowerShell run `Set-ExecutionPolicy -Scope Process Bypass`, followed by `./scripts/windows-setup.ps1`.
4. Start API: `./scripts/windows-start-api.ps1`.
5. Start Angular in another terminal: `./scripts/windows-start-frontend.ps1`.
6. Visit `http://127.0.0.1:4200` and `http://127.0.0.1:8000/docs`.

## Evaluation files

- Database ER diagram: `database/er_diagram.svg` and `database/er_diagram.pdf`.
- MySQL DDL: `database/schema_mysql.sql` (documentation/empty database only; Alembic is the normal installer).
- OpenAPI: `docs/openapi.json` and live `/openapi.json`.
- Postman: `docs/PREVIA_Postman_Collection.json`.
- CRUD: `backend/app/planning_crud.py` and `frontend/src/app/features/admin/planning.ts`.
- Tests: `backend/tests/test_flask_final.py` and `scripts/windows-tests.ps1`.
- Final report: `docs/FINAL_PROJECT_REPORT.md` (plus PDF distributed with package).
- Slides outline: `docs/EXPOSICION_15_MIN.md`.
- Completion checklist: `docs/VERIFICATION_CHECKLIST.md`.

## Migration transparency

The academic domain logic was originally written for FastAPI. The final Windows entrypoint `backend/app/flask_api.py` serves the API using Flask and reuses the existing handlers via an adapter; the admin CRUD is implemented as a native Flask-SQLAlchemy Blueprint. Some FastAPI imports remain in legacy code and tests. This approach is a conservative functional migration, **not a complete codebase rewrite**.

No local database is included in the ZIP and the package has not been pushed to GitHub. Do not use PREVIA for real enrollment decisions.

## H08 — Portales separados: estudiante y administrador

La navegación de PREVIA se separó en dos entornos basados en el rol guardado en MySQL.

- Estudiante: `estudiante.demo@estudiantes.example.test` — perfil, habilitadas, selección e historial.
- Administrador: `admin.demo@estudiantes.example.test` — panel de demanda, CSV y CRUD de planificación.
- Los dos accesos emplean códigos OTP temporales recibidos en Mailpit; **no se usan contraseñas fijas**.

En Windows 11, después de actualizar la carpeta del proyecto existente, ejecutar:

```powershell
.\scripts\windows-demo-accounts.ps1
.\scripts\windows-role-tests.ps1
```

Consultar [docs/ROLES_Y_CUENTAS_DE_PRUEBA.md](docs/ROLES_Y_CUENTAS_DE_PRUEBA.md). No borrar `.env` ni el volumen MySQL al aplicar la actualización.
