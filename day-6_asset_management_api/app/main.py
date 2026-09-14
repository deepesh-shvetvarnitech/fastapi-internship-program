from fastapi import FastAPI

from app.api.router import api_router

app = FastAPI(
    title="Company IT Asset Management API",
    description="Production-style employee IT asset management API using FastAPI dependencies.",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Assets",
            "description": "IT asset management operations.",
        },
        {
            "name": "Security",
            "description": "API key protected IT operations.",
        },
    ],
)

app.include_router(
    api_router,
    prefix="/api/v1",
)


@app.get("/", tags=["System"])
def root():
    return {
        "message": "Welcome to Company IT Asset Management API",
        "version": "1.0.0",
    }


@app.get("/health", tags=["System"])
def health():
    return {
        "status": "ok",
        "service": "asset-management-api",
    }