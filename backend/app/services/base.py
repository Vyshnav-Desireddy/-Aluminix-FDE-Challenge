from typing import Generic, TypeVar, Optional
from sqlalchemy.orm import Session

T = TypeVar('T')


class BaseService(Generic[T]):
    """Base service class for business logic."""
    
    def __init__(self, db: Session):
        self.db = db
