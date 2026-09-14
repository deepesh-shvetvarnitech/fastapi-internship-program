from fastapi import APIRouter

from app.api.routes.assets import router as asset_router

api_router = APIRouter()

api_router.include_router(asset_router)