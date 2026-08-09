from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Schema for chat request."""
    
    message: str = Field(..., description="User's chat message")


class ChatResponse(BaseModel):
    """Schema for chat response."""
    
    response: str = Field(..., description="AI response to the user's message")
