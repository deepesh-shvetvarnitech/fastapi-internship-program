
from fastapi import FastAPI


from app.api.router import api_router


app = FastAPI(
    title="IT Helpdesk Ticket Management API",
    description="Modular FastAPI application for IT helpdesk ticket management",
    version="1.0.0"
)


@app.get(
    "/health",
    tags=["SYSTEM"],
    summary="Health Check",
    description="Checks whether the Helpdesk API is running"
)
def health_check():
    
    return {"status": "healthy"}

app.include_router(
    api_router,
    prefix="/api/v1"
)