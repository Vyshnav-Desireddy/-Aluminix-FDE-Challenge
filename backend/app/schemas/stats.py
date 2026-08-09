from typing import Dict
from pydantic import BaseModel


class TaskStats(BaseModel):
    """Schema for task statistics."""
    
    total_tasks: int
    by_category: Dict[str, int]
    by_assignee: Dict[str, int]
    by_priority: Dict[str, int]
    total_deal_value_inr: int
    average_confidence: float
