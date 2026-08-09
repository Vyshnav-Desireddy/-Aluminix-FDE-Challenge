from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from app.config import settings
from app.database import init_db
from app.utils.exceptions import AppException
from app.utils.logging import setup_logging
from app.api import tasks, users, classify, ingest, dashboard, chat, sample_emails
from app.schemas.task import VALID_ASSIGNEE_IDS, VALID_CATEGORIES, VALID_PRIORITIES

# Setup logging
logger = setup_logging()

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("Starting application...")
    init_db()
    logger.info("Database initialized successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down application...")


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle application exceptions."""
    logger.error(f"Application error: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors for enum values."""
    errors = exc.errors()
    for error in errors:
        field = error.get("loc", [""])[-1]
        received = error.get("input")
        
        if field == "assignee_id":
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "error": "invalid_enum_value",
                    "field": "assignee_id",
                    "received": received,
                    "allowed": VALID_ASSIGNEE_IDS
                }
            )
        elif field == "category":
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "error": "invalid_enum_value",
                    "field": "category",
                    "received": received,
                    "allowed": VALID_CATEGORIES
                }
            )
        elif field == "priority":
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "error": "invalid_enum_value",
                    "field": "priority",
                    "received": received,
                    "allowed": VALID_PRIORITIES
                }
            )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "Validation error", "details": errors}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "details": {} if not settings.DEBUG else {"message": str(exc)}
        }
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# Include routers
app.include_router(tasks.router, prefix="", tags=["tasks"])
app.include_router(users.router, prefix="", tags=["users"])
app.include_router(classify.router, prefix="", tags=["classification"])
app.include_router(ingest.router, prefix="", tags=["ingestion"])
app.include_router(dashboard.router, prefix="", tags=["dashboard"])
app.include_router(chat.router, prefix="", tags=["chat"])
app.include_router(sample_emails.router, prefix="", tags=["sample-emails"])
