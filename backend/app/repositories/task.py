from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.task import Task
from app.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    """Repository for Task data access operations."""
    
    def __init__(self, db: Session):
        super().__init__(Task, db)
    
    def get_by_task_id(self, task_id: str) -> Optional[Task]:
        """Get a task by task_id."""
        return self.db.query(Task).filter(Task.task_id == task_id).first()
    
    def get_by_candidate_id(self, candidate_id: str, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get all tasks for a specific candidate_id."""
        return self.db.query(Task).filter(Task.candidate_id == candidate_id).offset(skip).limit(limit).all()
    
    def get_by_candidate_with_filters(
        self,
        candidate_id: str,
        thread_id: Optional[str] = None,
        source_email_id: Optional[str] = None,
        assignee_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """Get tasks for a candidate with optional filters."""
        query = self.db.query(Task).filter(Task.candidate_id == candidate_id)
        
        if thread_id:
            query = query.filter(Task.thread_id == thread_id)
        if source_email_id:
            query = query.filter(Task.source_email_id == source_email_id)
        if assignee_id:
            query = query.filter(Task.assignee_id == assignee_id)
        
        return query.offset(skip).limit(limit).all()
    
    def get_by_source_email_and_candidate(self, source_email_id: str, candidate_id: str) -> Optional[Task]:
        """Get a task by source_email_id and candidate_id (for duplicate detection)."""
        return self.db.query(Task).filter(
            Task.source_email_id == source_email_id,
            Task.candidate_id == candidate_id
        ).first()
    
    def get_by_thread_and_candidate(self, thread_id: str, candidate_id: str) -> Optional[Task]:
        """Get a task by thread_id and candidate_id (for thread reconciliation)."""
        return self.db.query(Task).filter(
            Task.thread_id == thread_id,
            Task.candidate_id == candidate_id
        ).first()
    
    def delete_by_task_id(self, task_id: str) -> bool:
        """Delete a task by task_id."""
        task = self.get_by_task_id(task_id)
        if task:
            self.db.delete(task)
            self.db.commit()
            return True
        return False
