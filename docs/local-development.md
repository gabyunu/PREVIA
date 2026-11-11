# Ejecución local en Ubuntu — H01

## Requisitos

Usar Python 3.14 con soporte `venv`, Node.js compatible con Angular 22 y npm.
Se verificó en este entorno con Python 3.14.4, Node 26.13.1 y npm 11.20.0.
No se modificó la configuración global del sistema. Si faltan estos runtimes,
el operador debe instalarlos antes de seguir esta guía; las instrucciones no
presuponen repositorios apt adicionales ni instalan paquetes globales.

Angular 22 admite Node ^22.22.3, ^24.15.0 o ^26.0.0 y TypeScript >=6.0 <6.1:
[matriz oficial](https://angular.dev/reference/versions).
Las dependencias Python se instalaron y probaron con CPython 3.14, incluido el
wheel nativo `pydantic-core` para cp314. El archivo de bloqueo registra las
versiones verificadas; no constituye una garantía para otras plataformas.

## Frontend

Desde la raíz del repositorio:

```bash
cd frontend
npm ci
npm run build
npm start
```

Abrir http://127.0.0.1:4200. El build de producción queda en
`frontend/dist/previa/browser/`. El CLI es local, no requiere instalar `ng`
globalmente. `package-lock.json` fija dependencias transitivas. La configuración
estricta de TypeScript está en `tsconfig.json`.

## Backend

En otra terminal, desde la raíz:

```bash
cd backend
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.lock
python -m pip install --no-deps -e .
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

`requirements.lock` incluye ejecución y desarrollo con versiones exactas.
`pyproject.toml` declara dependencias directas y el backend de construcción
Setuptools, descargado por pip en un entorno de construcción aislado.
Para resolver versiones nuevas deliberadamente se puede usar
`python -m pip install -e '.[dev]'`; revisar y regenerar el bloqueo después.

Comprobar desde otra terminal:

```bash
curl --fail http://127.0.0.1:8000/health
```

Respuesta: `{"status":"ok"}` con HTTP 200. Swagger local:
http://127.0.0.1:8000/docs. `/health` verifica el proceso API; no comprueba
persistencia ni otros servicios. Detener los servicios con Ctrl+C.

## Verificaciones

Dentro de `backend/`, con el entorno activado:

```bash
python -m pytest -q
ruff check .
ruff format --check .
python -m pip check
```

Dentro de `frontend/`: `npm run build`. No se incorporaron pruebas unitarias
frontend en H01. La prueba backend usa HTTPX con transporte ASGI; el arranque
HTTP con Uvicorn se verifica por separado.

## Configuración y alcance

No se necesitan variables ni secretos en H01, por eso no existe `.env.example`.
Se añadirá cuando una tarea autorizada requiera configuración. `.gitignore`
excluye `.env*` (permite `.env.example`), entornos virtuales, `node_modules`,
builds, cachés, metadatos Python, logs y archivos temporales.

No hay integración frontend/API todavía; no se requiere configurar CORS.
SQLAlchemy, MySQL, migraciones, Compose y correo quedan pendientes para los hitos
correspondientes. Los dominios institucionales, la malla, las fechas y la política
de privacidad siguen pendientes; H01 no los utiliza ni modifica D01–D06.

## Interfaz visual H01-B

H01-B adapta la referencia visual anterior a Angular 22. Con las dependencias
existentes basta `cd frontend` y `npm start`; abrir http://127.0.0.1:4200.
No requiere iniciar el backend. Incluye Inicio, Selección de asignaturas,
Mi selección, Historial y Demanda. Los datos son sintéticos; los cambios solo
viven en memoria y se pierden al recargar. No se guardan ni envían solicitudes.
Véanse [alcance, diferencias y verificaciones](h01-b-migration.md).
