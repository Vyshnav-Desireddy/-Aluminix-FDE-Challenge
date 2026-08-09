from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class EmailInput(BaseModel):
    """Schema for email input to classification engine."""
    
    email_id: str = Field(..., description="Unique email identifier")
    thread_id: str = Field(..., description="Thread identifier")
    from_name: str = Field(..., description="Sender name")
    from_email: EmailStr = Field(..., description="Sender email address")
    to: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body content")
    received_at: Optional[datetime] = Field(None, description="Email received timestamp")
