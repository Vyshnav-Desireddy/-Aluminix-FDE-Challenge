from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.email import EmailInput
from app.schemas.ingestion import IngestionResponse
from app.services.ingestion_service import IngestionService

router = APIRouter()


@router.post("/ingest", response_model=IngestionResponse)
def ingest_email(email: EmailInput, db: Session = Depends(get_db)):
    """
    Ingest an email for classification and task creation.
    
    This endpoint:
    1. Validates the email input
    2. Checks for duplicate emails (idempotency)
    3. Classifies the email using Gemini
    4. Applies deterministic safety/routing rules
    5. Creates a task if the email is actionable (is_task=true)
    6. Returns a structured response indicating the outcome
    
    Status values:
    - "created": A new task was created
    - "ignored": Email was classified as non-task (e.g., newsletter, spam)
    - "duplicate": Email was already processed and task exists
    """
    ingestion_service = IngestionService(db)
    return ingestion_service.ingest_email(email)
