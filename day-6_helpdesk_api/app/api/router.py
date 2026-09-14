from fastapi import APIRouter

from app.api.routes.tickets import router as tickets_router


api_router = APIRouter()


api_router.include_router(
    tickets_router
)