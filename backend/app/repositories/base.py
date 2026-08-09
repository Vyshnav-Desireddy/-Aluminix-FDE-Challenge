from typing import Generic, TypeVar, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """Base repository class for data access operations."""
    
    def __init__(self, model: type[T], db: Session):
        self.model = model
        self.db = db
    
    def get_by_id(self, id: str) -> Optional[T]:
        """Get a single record by ID."""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all records with pagination."""
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, obj: T) -> T:
        """Create a new record."""
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def update(self, obj: T) -> T:
        """Update an existing record."""
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def delete(self, id: str) -> bool:
        """Delete a record by ID."""
        obj = self.get_by_id(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False
