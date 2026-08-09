from sqlalchemy.orm import Session
from app.schemas.email import EmailInput
from app.schemas.ingestion import IngestionResponse
from app.schemas.task import TaskCreate, TaskResponse
from app.schemas.classification import ClassificationResult
from app.services.classification_service import ClassificationService
from app.services.task import TaskService
from app.repositories.task import TaskRepository
from app.config import settings
from app.utils.logging import setup_logging
from app.utils.exceptions import ConflictException

logger = setup_logging()


class IngestionService:
    """Service for email ingestion orchestration."""
    
    def __init__(self, db: Session):
        """Initialize ingestion service with database session."""
        self.db = db
        self.classification_service = ClassificationService()
        self.task_service = TaskService(db)
        self.task_repository = TaskRepository(db)
    
    def ingest_email(self, email: EmailInput) -> IngestionResponse:
        """
        Ingest an email through the complete pipeline:
        1. Validate email (handled by EmailInput schema)
        2. Check duplicate/idempotency (same email_id)
        3. Check thread reconciliation (same thread_id, different email_id)
        4. Classify email
        5. Apply safety validation
        6. Create or update task if actionable
        """
        # Step 1: Check for duplicate (idempotency) - same email_id
        existing_task = self.task_repository.get_by_source_email_and_candidate(
            source_email_id=email.email_id,
            candidate_id=settings.CANDIDATE_ID
        )
        
        if existing_task:
            logger.info(f"Duplicate email detected: {email.email_id}, returning existing task")
            return IngestionResponse(
                status="duplicate",
                task=TaskResponse.model_validate(existing_task),
                classification=None
            )
        
        # Step 2: Check for thread reconciliation - same thread_id, different email_id
        thread_task = self.task_repository.get_by_thread_and_candidate(
            thread_id=email.thread_id,
            candidate_id=settings.CANDIDATE_ID
        )
        
        # Step 3: Classify email
        try:
            classification = self.classification_service.classify_email(email)
        except ValueError as e:
            # If classification fails (e.g., Gemini not available), use triage fallback
            logger.warning(f"Classification failed for email {email.email_id}: {e}, using triage fallback")
            classification = self._create_triage_fallback(email)
        
        # Step 4: Handle non-task emails
        if not classification.is_task:
            logger.info(f"Email {email.email_id} classified as non-task, ignoring")
            return IngestionResponse(
                status="ignored",
                task=None,
                classification=classification
            )
        
        # Step 5: Thread reconciliation - update existing task in same thread
        if thread_task:
            logger.info(f"Thread reconciliation: updating existing task {thread_task.task_id} for thread {email.thread_id}")
            from app.schemas.task import TaskUpdate
            
            # Update relevant fields from the new classification
            update_data = TaskUpdate(
                title=self._generate_task_title(email, classification),
                description=email.body,  # Update description with latest email
                assignee_id=classification.assignee_id,
                category=classification.category,
                priority=classification.priority,
                due_date=classification.deadline,
                deal_value_inr=classification.deal_value_inr,
                company_name=classification.company_name,
                confidence=classification.confidence
            )
            
            updated_task = self.task_service.update_task(thread_task.task_id, update_data)
            
            return IngestionResponse(
                status="updated",  # New status for thread reconciliation
                task=TaskResponse.model_validate(updated_task),
                classification=classification
            )
        
        # Step 6: Create new task for actionable email (new thread)
        task_data = TaskCreate(
            candidate_id=settings.CANDIDATE_ID,  # Always from configuration
            source_email_id=email.email_id,  # Map email_id to source_email_id
            thread_id=email.thread_id,
            title=self._generate_task_title(email, classification),
            description=email.body,
            assignee_id=classification.assignee_id,  # From classification
            category=classification.category,  # From classification
            priority=classification.priority,  # From classification
            due_date=classification.deadline,  # From classification
            deal_value_inr=classification.deal_value_inr,  # From classification
            company_name=classification.company_name,  # From classification
            confidence=classification.confidence  # From classification
        )
        
        try:
            task = self.task_service.create_task(task_data)
            logger.info(f"Created task {task.task_id} for email {email.email_id}")
            
            return IngestionResponse(
                status="created",
                task=TaskResponse.model_validate(task),
                classification=classification
            )
        except ConflictException:
            # Handle race condition where task was created between our check and creation
            logger.warning(f"Race condition: task already exists for email {email.email_id}")
            existing_task = self.task_repository.get_by_source_email_and_candidate(
                source_email_id=email.email_id,
                candidate_id=settings.CANDIDATE_ID
            )
            return IngestionResponse(
                status="duplicate",
                task=TaskResponse.model_validate(existing_task),
                classification=classification
            )
    
    def _generate_task_title(self, email: EmailInput, classification: ClassificationResult) -> str:
        """Generate a task title from email and classification."""
        if classification.company_name:
            return f"{email.subject} - {classification.company_name}"
        return email.subject
    
    def _create_triage_fallback(self, email: EmailInput) -> ClassificationResult:
        """Create a triage fallback classification when Gemini is unavailable."""
        from app.schemas.classification import ClassificationResult
        return ClassificationResult(
            category="triage",
            assignee_id="u_triage",
            priority="medium",
            company_name=None,
            deal_value_inr=None,
            deadline=None,
            confidence=0.5,
            is_task=True,  # Still create task for triage review
            reason="Classification service unavailable, routed to triage for manual review"
        )
