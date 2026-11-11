# H01 — Estructura inicial y verificaciones

Fecha: 2026-11-11. **Confirmado:** autorización del usuario limitada a H01,
Angular 22 y Python 3.14. Se revisaron AGENTS.md y los documentos de requisitos,
decisiones, arquitectura, roadmap y modelo, además de planning-review.md.
Los textos de fase 0 describen el estado anterior; esta autorización no aprueba
H02 ni las recomendaciones funcionales/técnicas futuras.

## Archivos principales

```text
frontend/
  angular.json, package.json, package-lock.json
  tsconfig.json, tsconfig.app.json, tsconfig.spec.json
  src/
    index.html, main.ts, styles.css
    app/
      app.ts, app.html, app.config.ts, app.routes.ts
      features/home/home.ts, home.html
  public/favicon.ico
backend/
  pyproject.toml, requirements.lock, .python-version
  app/
    __init__.py, main.py
    api/
      __init__.py
      routes/__init__.py, health.py
  tests/test_health.py
docs/
  local-development.md
  h01-verification.md
```

También se actualizan README.md y .gitignore. Angular CLI generó su configuración
local de editor y formato. `.venv/`, `node_modules/` y `dist/` son artefactos
locales ignorados. No se añadieron variables de entorno sin uso.

## Dependencias instaladas

Frontend: Angular 22.2.5; CLI/build 22.2.6; TypeScript 6.0.3; RxJS 7.8.2;
tslib 2.9.1; Prettier 3.10.0. Incluye paquetes Angular common, compiler, core,
forms, platform-browser, router y compiler-cli. Versiones transitivas en
`frontend/package-lock.json`.

Backend: FastAPI 0.162.4, Pydantic 2.14.3 (pydantic-core 2.50.4), Uvicorn 0.54.0;
desarrollo: pytest 9.2.0, HTTPX 0.28.1 y Ruff 0.17.4. Versiones transitivas en
`backend/requirements.lock`. Instaladas dentro de `backend/.venv` con Python
3.14.4; no se instalaron SQLAlchemy, MySQL ni Alembic.

## Comandos y resultados reales

- `npm exec --yes --package=@angular/cli@22.2.6 -- ng new previa --directory frontend --routing --style=css --ssr=false --skip-git --skip-install --skip-tests --defaults --package-manager=npm`: proyecto creado.
- `python3.14 -m venv backend/.venv`: entorno creado.
- `backend/.venv/bin/python -m pip install -e './backend[dev]'`: instalación correcta.
- En frontend, `npm install --no-fund --no-audit`: 241 paquetes instalados.
- `npm install --package-lock-only --ignore-scripts --offline --no-audit --no-fund`: bloqueo sincronizado con package.json.
- `npm ls --depth=0`: dependencias resueltas sin conflictos.
- En frontend, `npm run build`: exit 0, build de producción correcto;
  tamaño inicial 191.19 kB, transferencia estimada 52.35 kB.
- En backend, `.venv/bin/python -m pytest -q`: exit 0, **1 passed** (0.30 s), sin warnings finales.
- `.venv/bin/ruff check .`: exit 0, `All checks passed!`.
- `.venv/bin/ruff format --check .`: exit 0, `6 files already formatted`.
- `.venv/bin/python -m pip check`: exit 0, `No broken requirements found`.
- Arranque real mediante subprocess del comando
  `backend/.venv/bin/python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000`:
  inicio completo; consulta con `urllib.request.urlopen` a
  `http://127.0.0.1:8000/health`: HTTP 200 y `{"status":"ok"}`;
  cierre del proceso de prueba correcto.

## Problemas y límites

El sandbox restringió red, pytest y sockets locales. Las descargas y las
verificaciones afectadas se repitieron con permisos ampliados. El build Angular
pasó dentro del sandbox, aunque el entorno emitió mensajes `Failed to create
stream fd: Operation not permitted` ajenos al resultado del compilador.

npm 11 avisó sobre scripts de instalación no aprobados de cuatro paquetes
opcionales/nativos; no se habilitaron globalmente. La compilación funcionó.
No se ejecutó auditoría de vulnerabilidades ni prueba visual en navegador.

La primera prueba con TestClient pasó con advertencia de deprecación de Starlette;
se reemplazó por HTTPX ASGITransport y se verificó de nuevo sin esa advertencia.
La compatibilidad comprobada corresponde a este entorno Ubuntu/CPython 3.14;
no se afirma haber probado otros sistemas.

**Pendiente:** H02 requiere autorización independiente. No se implementaron
persistencia, autenticación ni reglas académicas. La fase 1 completa no se declara
terminada: únicamente se entrega H01 para revisión.
