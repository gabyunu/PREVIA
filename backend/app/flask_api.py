"""Production Flask REST app for PREVIA.

Legacy domain handlers are reused through a narrowly scoped HTTP adapter so that
existing validation/versioning semantics remain unchanged. New administrative CRUD
uses native Flask-SQLAlchemy ORM models and transactions.

Entry point: python -m flask --app app.flask_api:app run --host 127.0.0.1 --port 8000
"""

from __future__ import annotations

from functools import wraps
from types import SimpleNamespace
from typing import Callable

from flask import Flask, Response as FlaskResponse, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from pydantic import ValidationError
from sqlalchemy.engine import URL
from starlette.responses import Response as StarletteResponse

from app import academic, auth, demand, drafts, history
from app.db import models as m
from app.db.session import database_url

# The same SQLAlchemy MetaData is shared by Alembic, the existing domain layer,
# and Flask-SQLAlchemy. Do NOT issue create_all: migrations own the schema.
db = SQLAlchemy(model_class=m.Base)


def error(status: int, code: str, message: str):
    return jsonify(error={"codigo": code, "mensaje": message}), status


def input_json(model):
    if not request.is_json:
        raise ValueError("Se requiere un cuerpo JSON.")
    value = request.get_json(silent=True)
    if not isinstance(value, dict):
        raise ValueError("El cuerpo debe ser un objeto JSON.")
    return model.model_validate(value)


def req():
    """Read-only view matching the fields required by existing domain handlers."""
    return SimpleNamespace(
        method=request.method,
        headers=request.headers,
        cookies=request.cookies,
        client=SimpleNamespace(host=request.remote_addr or "127.0.0.1"),
    )


def convert(value):
    if isinstance(value, StarletteResponse):
        # Starlette stores multiple Set-Cookie headers in raw_headers. A normal
        # dict would silently collapse them and break the session/CSRF cookies.
        result = FlaskResponse(value.body, status=value.status_code)
        result.headers.clear()
        for key, content in value.raw_headers:
            result.headers.add(key.decode("latin-1"), content.decode("latin-1"))
        return result
    if hasattr(value, "model_dump"):
        return jsonify(value.model_dump(mode="json"))
    return jsonify(value)


def positive(name: str, default=None, *, min_value=1, max_value=None):
    raw = request.args.get(name)
    if raw is None or raw == "":
        return default
    if not raw.isdecimal():
        raise ValueError(f"Parámetro '{name}' inválido.")
    value = int(raw)
    if value < min_value or (max_value is not None and value > max_value):
        raise ValueError(f"Parámetro '{name}' fuera de rango.")
    return value


def enum(name, choices, default=None):
    val = request.args.get(name, default)
    if val not in choices:
        raise ValueError(f"Parámetro '{name}' inválido.")
    return val


def register(app: Flask, rule: str, method: str, handler: Callable, body=None):
    @wraps(handler)
    def view(**kwargs):
        try:
            data = input_json(body) if body is not None else None
            if body is None:
                result = handler(req(), **kwargs)
            elif handler in (auth.request_otp, auth.verify_otp):
                # Identity handlers were written with (body, request) order.
                result = handler(data, req(), **kwargs)
            else:
                result = handler(req(), body=data, **kwargs)
            return convert(result)
        except (ValueError, ValidationError):
            # Never echo secret-containing request bodies or authentication tokens.
            return error(422, "entrada_invalida", "Revisa el formato de los datos enviados.")

    app.add_url_rule(rule, endpoint=f"{method}_{handler.__name__}_{len(app.view_functions)}", view_func=view, methods=[method])


def create_app(database_uri: str | URL | None = None):
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI=database_uri or database_url().render_as_string(hide_password=False),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JSON_SORT_KEYS=False,
    )
    db.init_app(app)

    # One exact origin, and explicit credentials. No wildcard CORS for OTP.
    @app.after_request
    def cors(response):
        origin = request.headers.get("Origin")
        if origin == auth.os.environ.get("AUTH_FRONTEND_ORIGIN", "http://127.0.0.1:4200"):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Headers"] = (
                "Content-Type, X-CSRF-Token, Idempotency-Key"
            )
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Expose-Headers"] = "Retry-After"
            response.headers["Vary"] = "Origin"
        return response

    @app.before_request
    def preflight():
        if request.method == "OPTIONS":
            return FlaskResponse(status=204)

    @app.before_request
    def enforce_separate_roles():
        """Protect student and administrator API namespaces at the server boundary.

        Client menus and Angular route guards are presentation, not authorization.
        The identity and roles are always read from the database-backed session.
        """
        if request.method == "OPTIONS":
            return None
        route = request.path
        if route.startswith("/api/v1/me/"):
            required = "estudiante"
        elif route.startswith("/api/v1/admin/"):
            required = "administrador"
        else:
            return None
        conn = db.session.connection()
        identity = auth.current(conn, req())
        if identity is None:
            db.session.rollback()
            return error(401, "sesion_requerida", "Inicia sesión para continuar.")
        roles = auth.user_data(conn, identity[1])["roles"]
        if set(roles) != {required}:
            db.session.rollback()
            return error(403, "permiso_requerido", "Tu cuenta no tiene acceso a esta sección.")
        return None

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    # Existing domain logic; Flask is the HTTP server and Flask-SQLAlchemy
    # manages the engine and metadata. FastAPI is NOT started for this app.
    register(app, "/api/v1/auth/otp/request", "POST", auth.request_otp, auth.EmailBody)
    register(app, "/api/v1/auth/otp/verify", "POST", auth.verify_otp, auth.VerifyBody)
    register(app, "/api/v1/me", "GET", auth.me)
    register(app, "/api/v1/auth/logout", "POST", auth.logout)
    register(app, "/api/v1/careers", "GET", academic.careers)

    @app.get("/api/v1/curricula")
    def curricula():
        try:
            return convert(academic.curricula(req(), career_id=positive("career_id")))
        except ValueError as exc:
            return error(422, "entrada_invalida", str(exc))

    register(app, "/api/v1/curricula/<int:curriculum_id>", "GET", academic.curriculum)
    register(app, "/api/v1/me/eligibility", "GET", academic.get_eligibility)
    register(app, "/api/v1/me/academic-profile", "GET", academic.get_profile)
    register(app, "/api/v1/me/academic-profile", "PUT", academic.put_profile, academic.ProfileBody)
    register(app, "/api/v1/periods", "GET", drafts.periods)

    @app.get("/api/v1/me/requests/<int:period_id>")
    def draft_read(period_id):
        try:
            raw = enum("allow_empty", ("true", "false", "True", "False", None), None)
            return convert(drafts.get_draft(req(), period_id, allow_empty=raw in {"true", "True"}))
        except ValueError as exc:
            return error(422, "entrada_invalida", str(exc))

    register(app, "/api/v1/me/requests/<int:period_id>/draft", "PUT", drafts.put_draft, drafts.Draft)
    register(app, "/api/v1/me/requests/<int:period_id>/submit", "POST", drafts.submit, drafts.Submit)

    @app.get("/api/v1/me/request-history")
    def history_all():
        try:
            return convert(history.history(req(), offset=positive("offset", 0, min_value=0), limit=positive("limit", 10, min_value=1, max_value=50)))
        except ValueError as exc:
            return error(422, "entrada_invalida", str(exc))

    @app.get("/api/v1/me/request-history/<int:request_id>/versions")
    def history_versions(request_id):
        try:
            return convert(history.versions(req(), request_id, offset=positive("offset", 0, min_value=0), limit=positive("limit", 10, min_value=1, max_value=50)))
        except ValueError as exc:
            return error(422, "entrada_invalida", str(exc))

    register(app, "/api/v1/me/request-history/<int:request_id>/versions/<int:version_id>", "GET", history.detail)
    register(app, "/api/v1/admin/demand/options", "GET", demand.options)

    @app.get("/api/v1/admin/demand")
    def demand_report():
        try:
            text = request.args.get("q", "")
            if len(text) > 255:
                raise ValueError("Búsqueda demasiado larga.")
            return convert(demand.demand(
                req(), periodo_id=positive("periodo_id"), malla_id=positive("malla_id"),
                q=text, semestre=positive("semestre"),
                prioridad=enum("prioridad", (None, "alta", "media", "baja")),
                orden=enum("orden", ("descending", "ascending", "name", "semester"), "descending"),
                tamano_grupo=positive("tamano_grupo", max_value=1000000),
                formato=enum("formato", ("json", "csv"), "json"),
            ))
        except ValueError as exc:
            return error(422, "entrada_invalida", str(exc))

    from app.planning_crud import planning_api
    app.register_blueprint(planning_api)

    @app.get("/openapi.json")
    def specification():
        from app.api_spec import spec
        return jsonify(spec())

    @app.get("/docs")
    def swagger():
        # Swagger UI assets are served by a public CDN; docs/postman collection
        # is provided in the repository for offline inspection.
        return """<!doctype html><html><head><meta charset='utf-8'>
        <title>PREVIA - Flask API</title>
        <link rel='stylesheet' href='https://unpkg.com/swagger-ui-dist@5/swagger-ui.css'></head>
        <body><div id='swagger-ui'></div>
        <script src='https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js'></script>
        <script>SwaggerUIBundle({url:'/openapi.json',dom_id:'#swagger-ui'});</script></body></html>"""

    return app


# CLI-compatible WSGI app. Loading the module initializes the Flask app only;
# no database mutations or network calls occur until a request/CLI command.
app = create_app()
