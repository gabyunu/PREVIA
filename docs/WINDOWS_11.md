# PREVIA on Windows 11 — clean installation

## 1. Prerequisites

Use **PowerShell** and install the following tools (prefer the official distributions):

```powershell
winget install --id Git.Git -e
winget install --id Microsoft.VisualStudioCode -e
winget install --id OpenJS.NodeJS.LTS -e
winget install --id astral-sh.uv -e
winget install --id Docker.DockerDesktop -e
```

**Important:** Docker Desktop is a graphical application. Start it after installation and configure **Linux containers using WSL 2**. If Windows asks for WSL setup, open PowerShell as Administrator and run `wsl --install`, then restart the laptop. Hardware virtualization must be enabled. Docker's official guide: https://docs.docker.com/desktop/setup/install/windows-install/ .

Angular in the ZIP requires Node **22.22.3+ (22.x), 24.15+, or 26.x**. Recommended: current compatible LTS. Use `node --version` and `npm.cmd --version` to verify. Python **3.14** is installed by `uv` during setup; installing Python separately is unnecessary.

Reopen PowerShell after WinGet changes the PATH.

## 2. Copy or clone the source

Recommended for the shared GitHub project:

```powershell
New-Item -ItemType Directory -Force "$HOME\Proyectos" | Out-Null
Set-Location "$HOME\Proyectos"
git clone https://github.com/gabyunu/PREVIA.git
Set-Location PREVIA
```

**Important:** this adaptation is supplied in a separate downloadable ZIP. Until the adapted files are pushed to GitHub, the original GitHub repository may still contain the old FastAPI entry point. To use **this exact version**, extract the provided `PREVIA-Final-Windows11.zip` to `C:\Users\<you>\Proyectos\PREVIA` or another folder you own, then `cd` to the extracted project root. Do not overwrite newer team changes without reviewing a Git diff.

## 3. First installation

In PowerShell, from the project directory:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\windows-setup.ps1
```

This script:

1. Checks the required programs and checks whether Docker Desktop is running.
2. Creates `.env` with random MySQL passwords and a local OTP HMAC key (only when `.env` does not exist).
3. Runs MySQL and Mailpit through Docker Compose.
4. Installs Python 3.14, creates `backend\.venv`, and installs the Flask API dependencies.
5. Runs the **existing Alembic migrations**, loads the provisional 53-course curriculum, and creates a demonstration academic period.
6. Runs `npm.cmd ci` and compiles the Angular frontend.

**Never** commit, send, or paste the contents of `.env`. Credentials from the older laptop are not needed on a clean new installation.

## 4. Start the application (two PowerShell terminals)

Terminal A — Flask + Flask-SQLAlchemy API:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\windows-start-api.ps1
```

Terminal B — Angular:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\windows-start-frontend.ps1
```

Open:

- GUI: http://127.0.0.1:4200
- Flask API: http://127.0.0.1:8000/health
- Swagger UI: http://127.0.0.1:8000/docs
- OpenAPI JSON (works offline): http://127.0.0.1:8000/openapi.json
- Mailpit: http://127.0.0.1:8025

Swagger UI loads JavaScript/CSS from a CDN, so it needs internet access. The included `docs/openapi.json` and `docs/PREVIA_Postman_Collection.json` can be opened without this dependency.

## 5. OTP test login and administrator

Use a fake academic email such as `demo@estudiantes.example.test`; a real university email is intentionally blocked. Copy the OTP from Mailpit.

To enable **administrator** permission in the local test database:

1. Log in once using a separate fictitious email, such as `admin@estudiantes.example.test`. This creates a local account.
2. Look up its ID via DBeaver (`previa_dev` → `usuario`) or a read-only SQL query.
3. Stop the API temporarily or use a new PowerShell window with environment loaded.
4. From `backend`, run:

   ```powershell
   .\.venv\Scripts\python.exe -m app.db.admin_access --user-id 2 --operator "classroom-demo" --confirm-local-test
   ```

   Replace **2** with the *actual* ID; never assume an ID. The account must not have academic history. This operation revokes existing sessions; log in again afterward.
5. Open **Administración · CRUD** and create, read, edit, and delete planned-seat records.

This changes only local test role assignments. Do not enable this in a deployed or institutional environment without proper provisioning and auditing.

## 6. Database inspection and testing

DBeaver MySQL connection:

- Host: `127.0.0.1`
- Port: `3307`
- Database: `previa_dev`
- User: value of `MYSQL_USER` in `.env`
- Password: value of `MYSQL_PASSWORD` in `.env`

Database diagram: `database/er_diagram.svg`, also inspectable directly in DBeaver.

Run tests from the project root:

```powershell
.\scripts\windows-tests.ps1
```

Do **not** run `backend/tests` with `PREVIA_TEST_MYSQL=1` against `previa_dev`: earlier MySQL integration tests intentionally mutate data, and some assume an isolated test database. The new `test_flask_final.py` uses isolated SQLite.

## 7. Common issues

- **Docker daemon not available:** open Docker Desktop and wait for it to finish starting; verify `docker info`.
- **Port already in use:** close other MySQL/Angular/API instances. Docker maps MySQL to host port **3307**, not 3306.
- **`npm.ps1` blocked:** use `npm.cmd` or set execution policy only for the current PowerShell process.
- **`ModuleNotFoundError`:** confirm `uv pip install --python backend/.venv/Scripts/python.exe -r backend/requirements-flask.txt` completed.
- **OTP not received:** inspect Mailpit at 8025 and ensure `docker compose ps` reports running services.
- **Admin access denied:** sign in as an account explicitly granted administrator role by `app.db.admin_access`; student sessions cannot manage planning.
- **No records from old laptop:** a ZIP/repository contains code, *not* the MySQL Docker volume. Export/import data separately only when authorized. Prefer new synthetic data for classroom demonstrations.

## 8. Security and limitations

Everything binds to `127.0.0.1` and is intended for **local classroom use only**. Flask's development server and the OTP Mailpit inbox are not deployment security solutions. Curriculum/prerequisites remain provisional and student academic statuses are self-reported.


## Accesos separados (actualización H08)

Para una instalación existente **no vuelvas a instalar todo ni elimines MySQL**. Extrae la actualización en la raíz del proyecto conservando `.env` y `backend/.venv`, y ejecuta:

```powershell
.\scripts\windows-demo-accounts.ps1
.\scripts\windows-role-tests.ps1
```

Entra desde `http://127.0.0.1:4200` como estudiante o administrador usando los correos de prueba. Los códigos de acceso se leen en `http://127.0.0.1:8025`. Consulta [ROLES_Y_CUENTAS_DE_PRUEBA.md](ROLES_Y_CUENTAS_DE_PRUEBA.md).
