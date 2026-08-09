from typing import Optional, List, Dict
from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.schemas.task import TaskResponse
from app.schemas.stats import TaskStats
from app.services.task import TaskService
from app.config import settings
from app.models.task import Task

router = APIRouter()


@router.get("/api/tasks", response_model=List[TaskResponse])
def get_dashboard_tasks(
    thread_id: Optional[str] = Query(None, description="Filter by thread_id"),
    assignee_id: Optional[str] = Query(None, description="Filter by assignee_id"),
    db: Session = Depends(get_db)
):
    """
    Get tasks for the dashboard using the configured CANDIDATE_ID.
    
    This endpoint automatically uses the CANDIDATE_ID from the environment configuration,
    making it suitable for frontend dashboard consumption without requiring the client
    to know the candidate ID.
    
    Optional filters:
    - thread_id: Filter tasks by thread ID
    - assignee_id: Filter tasks by assignee
    """
    service = TaskService(db)
    tasks = service.get_tasks(
        candidate_id=settings.CANDIDATE_ID,
        thread_id=thread_id,
        source_email_id=None,
        assignee_id=assignee_id
    )
    return tasks


@router.get("/api/stats", response_model=TaskStats)
def get_stats(db: Session = Depends(get_db)):
    """
    Get statistics for the dashboard using the configured CANDIDATE_ID.
    
    Returns aggregated statistics including:
    - total_tasks: Total number of tasks
    - by_category: Task count by category
    - by_assignee: Task count by assignee
    - by_priority: Task count by priority
    - total_deal_value_inr: Sum of all deal values
    - average_confidence: Average confidence score
    """
    # Get all tasks for the configured candidate
    tasks = db.query(Task).filter(Task.candidate_id == settings.CANDIDATE_ID).all()
    
    total_tasks = len(tasks)
    
    # Calculate statistics
    by_category: Dict[str, int] = {}
    by_assignee: Dict[str, int] = {}
    by_priority: Dict[str, int] = {}
    total_deal_value_inr = 0
    total_confidence = 0.0
    
    for task in tasks:
        # Count by category
        by_category[task.category] = by_category.get(task.category, 0) + 1
        
        # Count by assignee
        by_assignee[task.assignee_id] = by_assignee.get(task.assignee_id, 0) + 1
        
        # Count by priority
        by_priority[task.priority] = by_priority.get(task.priority, 0) + 1
        
        # Sum deal values
        if task.deal_value_inr:
            total_deal_value_inr += task.deal_value_inr
        
        # Sum confidence
        total_confidence += task.confidence
    
    # Calculate average confidence
    average_confidence = total_confidence / total_tasks if total_tasks > 0 else 0.0
    
    return TaskStats(
        total_tasks=total_tasks,
        by_category=by_category,
        by_assignee=by_assignee,
        by_priority=by_priority,
        total_deal_value_inr=total_deal_value_inr,
        average_confidence=average_confidence
    )
