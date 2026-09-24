from fastapi import FastAPI

from app.api.router import api_router


app = FastAPI(
    title="Employee Task Management API",
    description="FastAPI + SQLAlchemy 2.x + PostgreSQL CRUD API",
    version="1.0.0",
)


app.include_router(
    api_router,
    prefix="/api/v1",
)


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