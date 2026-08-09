from typing import Optional, Literal
from pydantic import BaseModel, Field
from datetime import date


# Reuse enum values from task schema
VALID_ASSIGNEE_IDS = [
    "u_aarti",
    "u_rohit",
    "u_meera",
    "u_karan",
    "u_divya",
    "u_triage"
]

VALID_CATEGORIES = [
    "enterprise_rfp",
    "smb_enquiry",
    "marketing",
    "alliances",
    "finance",
    "triage"
]

VALID_PRIORITIES = [
    "high",
    "medium",
    "low"
]

# Literal types for validation
AssigneeId = Literal["u_aarti", "u_rohit", "u_meera", "u_karan", "u_divya", "u_triage"]
Category = Literal["enterprise_rfp", "smb_enquiry", "marketing", "alliances", "finance", "triage"]
Priority = Literal["high", "medium", "low"]


class ClassificationResult(BaseModel):
    """Schema for classification result from Gemini."""
    
    category: Category = Field(..., description="Email category")
    assignee_id: AssigneeId = Field(..., description="Assigned user ID")
    priority: Priority = Field(..., description="Task priority")
    company_name: Optional[str] = Field(None, description="Extracted company name")
    deal_value_inr: Optional[int] = Field(None, description="Extracted deal value in INR")
    deadline: Optional[str] = Field(None, description="Extracted deadline (YYYY-MM-DD format)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Classification confidence")
    is_task: bool = Field(..., description="Whether this email should create a task")
    reason: str = Field(..., description="Short reason for classification")
