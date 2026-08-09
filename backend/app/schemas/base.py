from datetime import datetime
from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    """Base schema with common fields."""
    
    id: str = Field(..., description="Unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True
