import uuid
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.task import Task
from app.repositories.task import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate, VALID_ASSIGNEE_IDS, VALID_CATEGORIES, VALID_PRIORITIES
from app.utils.exceptions import NotFoundException, ConflictException, BadRequestException


class TaskService:
    """Service for Task business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = TaskRepository(db)
    
    def create_task(self, task_data: TaskCreate) -> Task:
        """Create a new task."""
        # Check for duplicate source_email_id for the same candidate
        existing = self.repository.get_by_source_email_and_candidate(
            task_data.source_email_id,
            task_data.candidate_id
        )
        if existing:
            raise ConflictException(
                f"Task with source_email_id '{task_data.source_email_id}' already exists for candidate '{task_data.candidate_id}'"
            )
        
        # Create new task
        task = Task(
            task_id=str(uuid.uuid4()),
            candidate_id=task_data.candidate_id,
            source_email_id=task_data.source_email_id,
            thread_id=task_data.thread_id,
            title=task_data.title,
            description=task_data.description,
            assignee_id=task_data.assignee_id,
            category=task_data.category,
            priority=task_data.priority,
            due_date=datetime.strptime(task_data.due_date, "%Y-%m-%d").date() if task_data.due_date else None,
            deal_value_inr=task_data.deal_value_inr,
            company_name=task_data.company_name,
            confidence=task_data.confidence,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        return self.repository.create(task)
    
    def get_task(self, task_id: str) -> Task:
        """Get a task by task_id."""
        task = self.repository.get_by_task_id(task_id)
        if not task:
            raise NotFoundException(f"Task with id '{task_id}' not found")
        return task
    
    def get_tasks(
        self,
        candidate_id: str,
        thread_id: Optional[str] = None,
        source_email_id: Optional[str] = None,
        assignee_id: Optional[str] = None
    ) -> List[Task]:
        """Get tasks for a candidate with optional filters."""
        return self.repository.get_by_candidate_with_filters(
            candidate_id=candidate_id,
            thread_id=thread_id,
            source_email_id=source_email_id,
            assignee_id=assignee_id
        )
    
    def update_task(self, task_id: str, task_data: TaskUpdate) -> Task:
        """Update an existing task."""
        task = self.get_task(task_id)
        
        # Update fields if provided
        if task_data.title is not None:
            task.title = task_data.title
        if task_data.description is not None:
            task.description = task_data.description
        if task_data.assignee_id is not None:
            task.assignee_id = task_data.assignee_id
        if task_data.category is not None:
            task.category = task_data.category
        if task_data.priority is not None:
            task.priority = task_data.priority
        if task_data.due_date is not None:
            task.due_date = datetime.strptime(task_data.due_date, "%Y-%m-%d").date()
        if task_data.deal_value_inr is not None:
            task.deal_value_inr = task_data.deal_value_inr
        if task_data.company_name is not None:
            task.company_name = task_data.company_name
        if task_data.confidence is not None:
            task.confidence = task_data.confidence
        
        task.updated_at = datetime.utcnow()
        
        return self.repository.update(task)
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task by task_id."""
        task = self.get_task(task_id)
        return self.repository.delete_by_task_id(task_id)
    
    def handle_enum_validation_error(self, field_name: str, received_value: str, error: Exception) -> dict:
        """Handle enum validation errors and return proper error response."""
        allowed_values = []
        if field_name == "assignee_id":
            allowed_values = VALID_ASSIGNEE_IDS
        elif field_name == "category":
            allowed_values = VALID_CATEGORIES
        elif field_name == "priority":
            allowed_values = VALID_PRIORITIES
        
        return {
            "error": "invalid_enum_value",
            "field": field_name,
            "received": received_value,
            "allowed": allowed_values
        }
