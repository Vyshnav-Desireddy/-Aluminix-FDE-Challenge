from datetime import datetime, date
from sqlalchemy import Column, String, Integer, Float, Date, Index, UniqueConstraint
from app.models.base import BaseModel


class Task(BaseModel):
    """Task model for storing sales inbox tasks."""
    
    __tablename__ = "tasks"
    
    task_id = Column(String, primary_key=True, index=True)
    candidate_id = Column(String, nullable=False, index=True)
    source_email_id = Column(String, nullable=False)
    thread_id = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    assignee_id = Column(String, nullable=False)
    category = Column(String, nullable=False)
    priority = Column(String, nullable=False)
    due_date = Column(Date, nullable=True)
    deal_value_inr = Column(Integer, nullable=True)
    company_name = Column(String, nullable=True)
    confidence = Column(Float, nullable=False)
    
    # Unique constraint to prevent duplicate tasks for same candidate + source_email_id
    __table_args__ = (
        UniqueConstraint('candidate_id', 'source_email_id', name='uq_candidate_source_email'),
    )
