from fastapi import APIRouter

from app.api.routes.employees import router as employee_router
from app.api.routes.tasks import router as task_router

api_router = APIRouter()

api_router.include_router(
    employee_router,
    prefix="/employees",
    tags=["Employees"]
)

api_router.include_router(
    task_router,
    prefix="/tasks",
    tags=["Tasks"]
)