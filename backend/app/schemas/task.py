from datetime import datetime, date
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict
from decimal import Decimal


# Valid enum values
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


class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    
    candidate_id: str = Field(..., description="Candidate email address")
    source_email_id: str = Field(..., description="Source email ID")
    thread_id: str = Field(..., description="Thread ID")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    assignee_id: AssigneeId = Field(..., description="Assignee user ID")
    category: Category = Field(..., description="Task category")
    priority: Priority = Field(..., description="Task priority")
    due_date: Optional[str] = Field(None, description="Due date in YYYY-MM-DD format")
    deal_value_inr: Optional[int] = Field(None, description="Deal value in INR")
    company_name: Optional[str] = Field(None, description="Company name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    
    @field_validator('candidate_id')
    @classmethod
    def normalize_candidate_id(cls, v: str) -> str:
        """Normalize candidate_id to lowercase and trim whitespace."""
        return v.strip().lower()
    
    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v: Optional[str]) -> Optional[str]:
        """Validate due_date format if provided."""
        if v is not None:
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("due_date must be in YYYY-MM-DD format")
        return v


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    
    model_config = ConfigDict(extra='forbid')
    
    title: Optional[str] = Field(None, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    assignee_id: Optional[AssigneeId] = Field(None, description="Assignee user ID")
    category: Optional[Category] = Field(None, description="Task category")
    priority: Optional[Priority] = Field(None, description="Task priority")
    due_date: Optional[str] = Field(None, description="Due date in YYYY-MM-DD format")
    deal_value_inr: Optional[int] = Field(None, description="Deal value in INR")
    company_name: Optional[str] = Field(None, description="Company name")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    
    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v: Optional[str]) -> Optional[str]:
        """Validate due_date format if provided."""
        if v is not None:
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("due_date must be in YYYY-MM-DD format")
        return v


class TaskResponse(BaseModel):
    """Schema for task response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    task_id: str
    candidate_id: str
    source_email_id: str
    thread_id: str
    title: str
    description: Optional[str] = None
    assignee_id: str
    category: str
    priority: str
    due_date: Optional[date] = None
    deal_value_inr: Optional[int] = None
    company_name: Optional[str] = None
    confidence: float
    created_at: datetime
    updated_at: datetime


class TaskCreateResponse(BaseModel):
    """Schema for task creation response."""
    
    task_id: str
    candidate_id: str
    source_email_id: str
    created_at: datetime


class EnumValidationError(BaseModel):
    """Schema for enum validation error response."""
    
    error: str = "invalid_enum_value"
    field: str
    received: str
    allowed: list[str]
