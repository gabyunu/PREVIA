"""Punto de entrada de la API local."""

import os

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes.health import router as health_router
from app.auth import router as auth_router

app = FastAPI(title="PREVIA", version="0.1.0")
app.include_router(health_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("AUTH_FRONTEND_ORIGIN", "http://127.0.0.1:4200")],
    allow_credentials=True,
    expose_headers=["Retry-After"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-CSRF-Token"],
)
app.include_router(auth_router)


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    # No devolver el cuerpo recibido: podría contener OTP u otros secretos.
    return JSONResponse(
        {
            "error": {
                "codigo": "entrada_invalida",
                "mensaje": "Revisa el formato de los datos enviados.",
            }
        },
        status_code=422,
    )
