from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from app.schemas.email import EmailInput
from app.services.sample_email_generator import SampleEmailGenerator

router = APIRouter()


@router.get("/sample-emails", response_model=List[EmailInput])
def generate_sample_emails(
    count: int = Query(1, ge=1, le=50, description="Number of sample emails to generate (1-50)"),
    category: Optional[str] = Query(None, description="Optional category filter"),
    shuffle: bool = Query(True, description="Whether to shuffle generated emails")
):
    """
    Generate sample sales emails for testing the ingestion pipeline.
    
    This endpoint generates realistic sample emails that can be submitted
    to the /ingest endpoint for testing the classification and task creation pipeline.
    
    Available categories:
    - enterprise_rfp: Enterprise RFPs and RFIs (high value, assigned to u_aarti)
    - smb_enquiry: SMB enquiries and demo requests (assigned to u_rohit)
    - marketing: Marketing, webinars, sponsorships (assigned to u_meera)
    - alliances: Reseller proposals, partnerships (assigned to u_karan)
    - finance: Invoices, payments, purchase orders (assigned to u_divya)
    - non_task: Non-actionable emails (newsletters, spam, auto-replies)
    
    The generated emails are valid inputs to the POST /ingest endpoint and
    will flow through the normal classification, routing, and task creation pipeline.
    """
    generator = SampleEmailGenerator()
    
    # Validate category if provided
    if category:
        available_categories = generator.get_available_categories()
        if category not in available_categories:
            available_str = ", ".join(available_categories)
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category '{category}'. Available categories: {available_str}"
            )
    
    return generator.generate_emails(count=count, category=category, shuffle=shuffle)


@router.get("/sample-emails/categories", response_model=List[str])
def get_sample_email_categories():
    """
    Get list of available sample email categories.
    
    Returns the list of categories that can be used to filter
    sample email generation.
    """
    generator = SampleEmailGenerator()
    return generator.get_available_categories()
