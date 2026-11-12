"""Identidad exclusivamente local. Ningún secreto se registra en logs."""

import hashlib
import hmac
import os
import re
import secrets
import smtplib
from datetime import UTC, datetime, timedelta
from email.message import EmailMessage
from functools import lru_cache

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import insert, select, update

from app.db import models as m
from app.db.session import make_engine

router = APIRouter(prefix="/api/v1")


def now():
    return datetime.now(UTC).replace(tzinfo=None, microsecond=0)


class Settings:
    def __init__(self):
        self.key = os.environ.get("AUTH_HMAC_KEY", "")
        if len(self.key) < 32:
            raise RuntimeError(
                "Configura AUTH_HMAC_KEY local de al menos 32 caracteres"
            )
        self.domains = set(
            os.environ.get("AUTH_ALLOWED_DOMAINS", "estudiantes.example.test")
            .lower()
            .split(",")
        )
        if any(not d.endswith((".test", ".invalid")) for d in self.domains):
            raise RuntimeError(
                "H02-B admite únicamente dominios ficticios .test/.invalid"
            )
        self.origin = os.environ.get("AUTH_FRONTEND_ORIGIN", "http://127.0.0.1:4200")
        self.secure = os.environ.get("AUTH_COOKIE_SECURE", "false").lower() == "true"
        self.smtp_host = os.environ.get("SMTP_HOST", "127.0.0.1")
        if self.smtp_host not in {"127.0.0.1", "localhost", "mailpit"}:
            raise RuntimeError("SMTP restringido a Mailpit local")
        self.smtp_port = int(os.environ.get("SMTP_PORT", "1025"))
        self.ttl = int(os.environ.get("AUTH_OTP_SECONDS", "600"))
        self.attempts = int(os.environ.get("AUTH_OTP_ATTEMPTS", "5"))
        self.cooldown = int(os.environ.get("AUTH_RESEND_SECONDS", "60"))
        self.email_limit = int(os.environ.get("AUTH_EMAIL_HOURLY", "5"))
        self.ip_limit = int(os.environ.get("AUTH_IP_HOURLY", "30"))
        self.session_seconds = int(os.environ.get("AUTH_SESSION_SECONDS", "28800"))
        self.idle_seconds = int(os.environ.get("AUTH_IDLE_SECONDS", "1800"))
        if (
            min(
                self.ttl,
                self.attempts,
                self.cooldown,
                self.email_limit,
                self.ip_limit,
                self.session_seconds,
                self.idle_seconds,
            )
            <= 0
        ):
            raise RuntimeError("Los límites de autenticación deben ser positivos")


@lru_cache
def settings():
    return Settings()


@lru_cache
def engine():
    return make_engine()


def digest(value):
    return hmac.new(settings().key.encode(), value.encode(), hashlib.sha256).hexdigest()


def error(status, code, message, retry=None):
    return JSONResponse(
        {"error": {"codigo": code, "mensaje": message}},
        status_code=status,
        headers={
            "Cache-Control": "no-store",
            **({"Retry-After": str(retry)} if retry else {}),
        },
    )


def denied():
    return error(
        401,
        "autenticacion_invalida",
        "Código incorrecto, vencido o ya utilizado. Solicita otro código.",
    )


class EmailBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    correo: str = Field(min_length=3, max_length=254)


class VerifyBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    desafio_id: str = Field(pattern=r"^[A-Za-z0-9_-]{32,64}$")
    codigo: str = Field(pattern=r"^[0-9]{8}$")


def normalize(email):
    email = email.strip()
    if not re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+", email):
        return None
    local, domain = email.rsplit("@", 1)
    if local.startswith(".") or local.endswith(".") or ".." in local or len(local) > 64:
        return None
    return local + "@" + domain.lower()


def origin_ok(request):
    return (
        request.headers.get("origin") == settings().origin
        and request.headers.get("sec-fetch-site") != "cross-site"
    )


def lock(conn):
    # Mutex transaccional compartido: serializa identidad en este entorno local.
    conn.execute(
        select(m.auth_control).where(m.auth_control.c.id == 1).with_for_update()
    ).one()


def event(conn, kind, user=None):
    conn.execute(
        insert(m.evento_seguridad).values(
            tipo=kind, actor_usuario_id=user, instante=now()
        )
    )


def rate(conn, scope, identity, maximum, cooldown=0):
    key = digest(scope + ":" + identity)
    row = (
        conn.execute(select(m.limite_auth).where(m.limite_auth.c.clave == key))
        .mappings()
        .first()
    )
    time = now()
    if row and (time - row["ventana_en"]).total_seconds() < 3600:
        wait = cooldown - (time - row["ultimo_en"]).total_seconds()
        if row["cantidad"] >= maximum or (cooldown > 0 and wait > 0):
            return max(
                1,
                int(
                    3600 - (time - row["ventana_en"]).total_seconds()
                    if row["cantidad"] >= maximum
                    else wait
                ),
            )
        conn.execute(
            update(m.limite_auth)
            .where(m.limite_auth.c.clave == key)
            .values(cantidad=row["cantidad"] + 1, ultimo_en=time)
        )
    elif row:
        conn.execute(
            update(m.limite_auth)
            .where(m.limite_auth.c.clave == key)
            .values(cantidad=1, ultimo_en=time, ventana_en=time)
        )
    else:
        conn.execute(
            insert(m.limite_auth).values(
                clave=key, cantidad=1, ultimo_en=time, ventana_en=time
            )
        )
    return 0


def send_code(email, code):
    message = EmailMessage()
    message["From"] = "PREVIA local <no-reply@example.test>"
    message["To"] = email
    message["Subject"] = "PREVIA — código de acceso local"
    message.set_content(
        f"Tu código de prueba es: {code}\nVigencia: {settings().ttl // 60} minutos.\n"
        "Solo desarrollo local. No certifica matrícula activa."
    )
    with smtplib.SMTP(settings().smtp_host, settings().smtp_port, timeout=5) as smtp:
        smtp.send_message(message)


@router.post("/auth/otp/request")
def request_otp(body: EmailBody, request: Request):
    if not origin_ok(request):
        return error(403, "origen_invalido", "Origen no autorizado.")
    email = normalize(body.correo)
    if email is None:
        return error(422, "correo_invalido", "Introduce un correo válido.")
    challenge = secrets.token_urlsafe(32)
    with engine().begin() as conn:
        lock(conn)
        wait = rate(conn, "emision_ip", request.client.host, settings().ip_limit)
        if not wait:
            wait = rate(
                conn,
                "emision_correo",
                email,
                settings().email_limit,
                settings().cooldown,
            )
        if wait:
            event(conn, "emision_limitada")
            return error(
                429, "limite_emision", "Espera antes de solicitar otro código.", wait
            )
        if email.rsplit("@", 1)[1] in settings().domains:
            time = now()
            code = f"{secrets.randbelow(100_000_000):08d}"
            conn.execute(
                update(m.desafio_otp)
                .where(
                    m.desafio_otp.c.correo_normalizado == email,
                    m.desafio_otp.c.consumido_en.is_(None),
                    m.desafio_otp.c.invalidado_en.is_(None),
                )
                .values(invalidado_en=time)
            )
            conn.execute(
                insert(m.desafio_otp).values(
                    id=challenge,
                    correo_normalizado=email,
                    proposito="acceso",
                    codigo_digest=digest(challenge + ":" + code),
                    emitido_en=time,
                    expira_en=time + timedelta(seconds=settings().ttl),
                    intentos=0,
                )
            )
            try:
                send_code(email, code)
            except OSError, smtplib.SMTPException:
                conn.execute(
                    update(m.desafio_otp)
                    .where(m.desafio_otp.c.id == challenge)
                    .values(invalidado_en=time)
                )
                event(conn, "smtp_fallo")
                return error(
                    503,
                    "correo_no_disponible",
                    "Correo local no disponible. Inténtalo después.",
                )
        event(conn, "otp_solicitado")
    return JSONResponse(
        {
            "mensaje": "Si el correo está autorizado, recibirás un código de acceso.",
            "desafio_id": challenge,
            "vigencia_segundos": settings().ttl,
        },
        status_code=202,
    )


def current(conn, request):
    token = request.cookies.get("previa_session", "")
    row = (
        conn.execute(select(m.sesion).where(m.sesion.c.token_digest == digest(token)))
        .mappings()
        .first()
    )
    time = now()
    if (
        not row
        or row["revocado_en"]
        or row["expira_en"] <= time
        or (time - row["ultimo_en"]).total_seconds() >= settings().idle_seconds
    ):
        return None
    user = (
        conn.execute(select(m.usuario).where(m.usuario.c.id == row["usuario_id"]))
        .mappings()
        .one()
    )
    if not user["activo"]:
        return None
    return row, user


def user_data(conn, user):
    roles = (
        conn.execute(
            select(m.rol.c.nombre)
            .join(m.usuario_rol)
            .where(m.usuario_rol.c.usuario_id == user["id"])
        )
        .scalars()
        .all()
    )
    return {"id": user["id"], "correo": user["correo_normalizado"], "roles": roles}


@router.post("/auth/otp/verify")
def verify_otp(body: VerifyBody, request: Request):
    if not origin_ok(request):
        return error(403, "origen_invalido", "Origen no autorizado.")
    with engine().begin() as conn:
        lock(conn)
        wait = rate(conn, "verificacion_ip", request.client.host, 50)
        if wait:
            event(conn, "verificacion_limitada")
            return error(
                429,
                "limite_intentos",
                "Demasiados intentos. Espera para continuar.",
                wait,
            )
        row = (
            conn.execute(
                select(m.desafio_otp).where(m.desafio_otp.c.id == body.desafio_id)
            )
            .mappings()
            .first()
        )
        time = now()
        if (
            not row
            or row["proposito"] != "acceso"
            or row["consumido_en"]
            or row["invalidado_en"]
            or row["expira_en"] <= time
            or row["intentos"] >= settings().attempts
        ):
            event(conn, "otp_rechazado")
            return denied()
        wait = rate(conn, "verificacion_correo", row["correo_normalizado"], 25)
        if wait:
            return error(
                429,
                "limite_intentos",
                "Demasiados intentos. Espera para continuar.",
                wait,
            )
        conn.execute(
            update(m.desafio_otp)
            .where(m.desafio_otp.c.id == row["id"])
            .values(intentos=row["intentos"] + 1)
        )
        if not hmac.compare_digest(
            row["codigo_digest"], digest(row["id"] + ":" + body.codigo)
        ):
            event(conn, "otp_rechazado")
            return denied()
        user = (
            conn.execute(
                select(m.usuario).where(
                    m.usuario.c.correo_normalizado == row["correo_normalizado"]
                )
            )
            .mappings()
            .first()
        )
        if user and not user["activo"]:
            event(conn, "cuenta_suspendida", user["id"])
            return denied()
        if not user:
            uid = conn.execute(
                insert(m.usuario).values(correo_normalizado=row["correo_normalizado"])
            ).inserted_primary_key[0]
            conn.execute(insert(m.perfil_estudiante).values(usuario_id=uid))
            role = conn.scalar(select(m.rol.c.id).where(m.rol.c.nombre == "estudiante"))
            conn.execute(insert(m.usuario_rol).values(usuario_id=uid, rol_id=role))
            user = (
                conn.execute(select(m.usuario).where(m.usuario.c.id == uid))
                .mappings()
                .one()
            )
            event(conn, "estudiante_creado", uid)
        conn.execute(
            update(m.desafio_otp)
            .where(m.desafio_otp.c.id == row["id"])
            .values(consumido_en=time)
        )
        # Rotar la sesión presentada sin aceptar identificadores elegidos por cliente.
        conn.execute(
            update(m.sesion)
            .where(
                m.sesion.c.token_digest
                == digest(request.cookies.get("previa_session", ""))
            )
            .values(revocado_en=time)
        )
        token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        conn.execute(
            insert(m.sesion).values(
                usuario_id=user["id"],
                token_digest=digest(token),
                csrf_digest=digest(csrf),
                creado_en=time,
                ultimo_en=time,
                expira_en=time + timedelta(seconds=settings().session_seconds),
            )
        )
        event(conn, "sesion_iniciada", user["id"])
        response = JSONResponse({"usuario": user_data(conn, user), "csrf_token": csrf})
        response.set_cookie(
            "previa_session",
            token,
            httponly=True,
            secure=settings().secure,
            samesite="strict",
            max_age=settings().session_seconds,
            path="/api/v1",
        )
        response.set_cookie(
            "previa_csrf",
            csrf,
            httponly=False,
            secure=settings().secure,
            samesite="strict",
            max_age=settings().session_seconds,
            path="/",
        )
        response.headers["Cache-Control"] = "no-store"
        return response


@router.get("/me")
def me(request: Request):
    with engine().begin() as conn:
        lock(conn)
        result = current(conn, request)
        if not result:
            return error(401, "sesion_requerida", "Inicia sesión para continuar.")
        session, user = result
        conn.execute(
            update(m.sesion)
            .where(m.sesion.c.id == session["id"])
            .values(ultimo_en=now())
        )
        return JSONResponse(
            user_data(conn, user), headers={"Cache-Control": "no-store"}
        )


@router.post("/auth/logout")
def logout(request: Request):
    if not origin_ok(request):
        return error(403, "origen_invalido", "Origen no autorizado.")
    with engine().begin() as conn:
        lock(conn)
        result = current(conn, request)
        if not result:
            return error(401, "sesion_requerida", "La sesión ha vencido.")
        session, user = result
        if not hmac.compare_digest(
            session["csrf_digest"], digest(request.headers.get("x-csrf-token", ""))
        ):
            return error(403, "csrf_invalido", "No se pudo validar la petición.")
        conn.execute(
            update(m.sesion)
            .where(m.sesion.c.id == session["id"])
            .values(revocado_en=now())
        )
        event(conn, "sesion_cerrada", user["id"])
    response = Response(status_code=204)
    response.delete_cookie(
        "previa_session",
        path="/api/v1",
        secure=settings().secure,
        httponly=True,
        samesite="strict",
    )
    response.delete_cookie(
        "previa_csrf", path="/", secure=settings().secure, samesite="strict"
    )
    return response
