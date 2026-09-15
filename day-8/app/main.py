from fastapi import FastAPI

from app.api.router import api_router
from app.db.base import Base
from app.db.models import Department, Employee, Task
from app.db.session import engine


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Employee & Task Management API",
    description="Day 8 FastAPI + SQLAlchemy + PostgreSQL CRUD API",
    version="1.0.0"
)

app.include_router(
    api_router,
    prefix="/api/v1"
)


@app.get("/")
def root():
    return {
        "message": "Employee & Task Management API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }