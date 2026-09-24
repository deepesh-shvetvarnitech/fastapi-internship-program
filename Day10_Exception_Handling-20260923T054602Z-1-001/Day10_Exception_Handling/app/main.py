# from fastapi import FastAPI

# from app.api.router import api_router


# app = FastAPI(
#     title="Employee Task Management API",
#     description="FastAPI + SQLAlchemy 2.x + PostgreSQL CRUD API",
#     version="1.0.0",
# )


# app.include_router(
#     api_router,
#     prefix="/api/v1",
# )


# @app.get(
#     "/",
#     tags=["System"],
# )
# def root():
#     return {
#         "message": "Employee Task Management API",
#         "version": "1.0.0",
#     }


# @app.get(
#     "/health",
#     tags=["System"],
# )
# def health():
#     return {
#         "status": "healthy",
#     }


import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError

from app.api.router import api_router
from app.core.exceptions import AppException
from app.core.exception_handlers import (
    app_exception_handler,
    generic_exception_handler,
    integrity_error_handler,
    validation_exception_handler,
)


app = FastAPI(
    title="Employee Task Management API",
    description="FastAPI + SQLAlchemy + PostgreSQL CRUD API",
    version="1.0.0",
)


# ============================================================
# REQUEST ID MIDDLEWARE
# ============================================================

@app.middleware("http")
async def request_id_middleware(
    request: Request,
    call_next,
):
    request_id = request.headers.get(
        "X-Request-ID"
    )

    if not request_id:
        request_id = f"req-{uuid.uuid4().hex[:12]}"

    request.state.request_id = request_id

    response = await call_next(request)

    response.headers["X-Request-ID"] = request_id

    return response


# ============================================================
# GLOBAL EXCEPTION HANDLERS
# ============================================================

app.add_exception_handler(
    AppException,
    app_exception_handler,
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.add_exception_handler(
    IntegrityError,
    integrity_error_handler,
)

app.add_exception_handler(
    Exception,
    generic_exception_handler,
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(
    api_router,
    prefix="/api/v1",
)


# ============================================================
# SYSTEM ENDPOINTS
# ============================================================

@app.get(
    "/",
    tags=["System"],
)
def root():
    return {
        "message": "Employee Task Management API",
        "version": "1.0.0",
    }


@app.get(
    "/health",
    tags=["System"],
)
def health():
    return {
        "status": "healthy",
    }