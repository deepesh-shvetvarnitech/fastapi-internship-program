
from fastapi import APIRouter

from app.api.routes.tickets import router as tickets_router
from app.api.routes.reports import router as reports_router


api_router = APIRouter()


api_router.include_router(tickets_router)
api_router.include_router(reports_router)