from sqlalchemy.orm import Session
from app.models.task import Task
from app.config import settings
from app.utils.logging import setup_logging
from google import genai
from google.genai import errors as genai_errors

logger = setup_logging()


class ChatService:
    """Service for grounded chat about tasks and sales inbox."""
    
    def __init__(self, db: Session):
        """Initialize chat service with database session."""
        self.db = db
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY) if settings.GEMINI_API_KEY else None
    
    def chat(self, message: str) -> str:
        """
        Process a chat message with context from the user's tasks.
        
        This provides a grounded chat experience by including relevant
        task context in the prompt sent to Gemini.
        """
        if not self.client:
            return "Chat service unavailable - GEMINI_API_KEY not configured"
        
        # Get user's tasks for context
        tasks = self.db.query(Task).filter(Task.candidate_id == settings.CANDIDATE_ID).all()
        
        # Build context from tasks
        context = self._build_task_context(tasks)
        
        # Build prompt with context
        prompt = f"""
You are a helpful assistant for a sales inbox task router. You help users understand their tasks and sales pipeline.

USER'S TASKS CONTEXT:
{context}

USER QUESTION:
{message}

Provide a helpful, concise response based on the task context above. If the question cannot be answered from the context, say so politely.
Keep responses under 200 words.
"""
        
        try:
            response = self.client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config={"temperature": 0.7}
            )
            
            return response.text.strip()
            
        except genai_errors.ClientError as e:
            # Check if it's a quota exceeded error (429)
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
                logger.error(f"Gemini API quota exceeded: {e}")
                return "Sorry, the AI service quota has been exceeded. Please try again later or upgrade your plan."
            else:
                logger.error(f"Gemini API error: {e}")
                return "Sorry, I encountered an error with the AI service. Please try again."
        except Exception as e:
            logger.error(f"Error in chat service: {e}")
            return "Sorry, I encountered an error processing your request. Please try again."
    
    def _build_task_context(self, tasks) -> str:
        """Build a summary of tasks for context."""
        if not tasks:
            return "No tasks found."
        
        total = len(tasks)
        
        # Count by category
        by_category = {}
        by_assignee = {}
        by_priority = {}
        
        for task in tasks:
            by_category[task.category] = by_category.get(task.category, 0) + 1
            by_assignee[task.assignee_id] = by_assignee.get(task.assignee_id, 0) + 1
            by_priority[task.priority] = by_priority.get(task.priority, 0) + 1
        
        # Build summary
        summary = f"Total tasks: {total}\n"
        summary += f"By category: {dict(by_category)}\n"
        summary += f"By assignee: {dict(by_assignee)}\n"
        summary += f"By priority: {dict(by_priority)}\n"
        
        # Add recent tasks (last 5)
        summary += "\nRecent tasks:\n"
        for task in tasks[-5:]:
            summary += f"- {task.title} (assignee: {task.assignee_id}, priority: {task.priority})\n"
        
        return summary
