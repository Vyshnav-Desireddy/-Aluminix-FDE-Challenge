from fastapi import APIRouter, HTTPException, status
from app.schemas.email import EmailInput
from app.schemas.classification import ClassificationResult
from app.services.classification_service import ClassificationService

router = APIRouter()


@router.post("/api/classify", response_model=ClassificationResult, status_code=status.HTTP_200_OK)
async def classify_email(email: EmailInput):
    """Classify an email using Gemini AI (development endpoint for testing)."""
    service = ClassificationService()
    
    if not service.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": "Gemini classifier not available", "message": "GEMINI_API_KEY not configured"}
        )
    
    try:
        classification = service.classify_email(email)
        return classification
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Classification error", "message": str(e)}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "message": str(e)}
        )
