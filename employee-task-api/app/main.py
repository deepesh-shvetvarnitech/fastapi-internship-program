from fastapi import FastAPI

app = FastAPI(
    title="Employee Task API",
    description="Backend service for employee and task management",
    version="1.0.0"
)


@app.get("/")
def root():
    """Welcome message."""
    return {"message": "Welcome to Employee Task API"}


@app.get("/health")
def health():
    """Check service health."""
    return {
        "status": "ok",
        "service": "employee-task-api"
    }


@app.get("/version")
def version():
    """Get application version."""
    return {
        "service": "employee-task-api",
        "version": "1.0.0",
        "environment": "development"
    }