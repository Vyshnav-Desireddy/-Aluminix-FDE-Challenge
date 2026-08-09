from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, status, Depends, Request
from sqlalchemy.orm import Session
from pydantic import ValidationError
from app.database import get_db
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskCreateResponse, EnumValidationError
from app.services.task import TaskService
from app.schemas.task import VALID_ASSIGNEE_IDS, VALID_CATEGORIES, VALID_PRIORITIES

router = APIRouter()


@router.post("/tasks", response_model=TaskCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task."""
    try:
        service = TaskService(db)
        task = service.create_task(task_data)
        return TaskCreateResponse(
            task_id=task.task_id,
            candidate_id=task.candidate_id,
            source_email_id=task.source_email_id,
            created_at=task.created_at
        )
    except Exception as e:
        # Handle conflict for duplicate source_email_id
        error_msg = str(e)
        if "already exists" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"error": "Duplicate task", "message": error_msg}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": str(e)}
            )


@router.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(
    candidate_id: str = Query(..., description="Candidate email address"),
    thread_id: Optional[str] = Query(None, description="Filter by thread_id"),
    source_email_id: Optional[str] = Query(None, description="Filter by source_email_id"),
    assignee_id: Optional[str] = Query(None, description="Filter by assignee_id"),
    db: Session = Depends(get_db)
):
    """Get tasks for a candidate with optional filters."""
    service = TaskService(db)
    tasks = service.get_tasks(candidate_id, thread_id, source_email_id, assignee_id)
    return tasks


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task_data: TaskUpdate, db: Session = Depends(get_db)):
    """Update an existing task."""
    try:
        service = TaskService(db)
        task = service.update_task(task_id, task_data)
        return task
    except Exception as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Task not found"}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": str(e)}
            )


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str, db: Session = Depends(get_db)):
    """Delete a task by task_id."""
    service = TaskService(db)
    try:
        service.delete_task(task_id)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Task not found"}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": str(e)}
            )
