from typing import Optional, Literal
from pydantic import BaseModel, Field
from app.schemas.task import TaskResponse
from app.schemas.classification import ClassificationResult


class IngestionResponse(BaseModel):
    """Schema for email ingestion response."""
    
    status: Literal["created", "ignored", "duplicate", "updated"] = Field(..., description="Ingestion status")
    task: Optional[TaskResponse] = Field(None, description="Created or existing task (if applicable)")
    classification: Optional[ClassificationResult] = Field(None, description="Classification result")
