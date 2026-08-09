from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter()


@router.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Grounded chat API for asking questions about tasks and sales pipeline.
    
    This endpoint uses Gemini AI to answer questions about the user's tasks,
    providing context from their actual task data for grounded responses.
    
    The chat is "grounded" because it includes relevant task context in the prompt,
    ensuring responses are based on actual data rather than hallucinations.
    """
    chat_service = ChatService(db)
    response = chat_service.chat(request.message)
    return ChatResponse(response=response)
