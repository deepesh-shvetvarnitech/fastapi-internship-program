from fastapi import FastAPI

from app.api.router import api_router


app = FastAPI(
    title="Helpdesk API",
    description="FastAPI Dependency Injection Assignment",
    version="1.0.0",
)


app.include_router(api_router)


@app.get("/")
def home():
    return {
        "message": "Helpdesk API is running"
    }