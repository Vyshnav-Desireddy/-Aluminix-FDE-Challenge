from datetime import datetime
from typing import Optional
from app.schemas.email import EmailInput
from app.schemas.classification import ClassificationResult, VALID_ASSIGNEE_IDS, VALID_CATEGORIES, VALID_PRIORITIES
from app.services.gemini_classifier import GeminiClassifier
from app.utils.logging import setup_logging

logger = setup_logging()


class ClassificationService:
    """Service for email classification with validation and routing safeguards."""
    
    def __init__(self):
        """Initialize classification service with Gemini classifier."""
        self.gemini = GeminiClassifier()
    
    def _validate_classification(self, classification: ClassificationResult) -> ClassificationResult:
        """Validate and sanitize classification result."""
        # Clamp confidence to valid range
        classification.confidence = max(0.0, min(1.0, classification.confidence))
        
        # Validate enum values (Pydantic should handle this, but double-check)
        if classification.assignee_id not in VALID_ASSIGNEE_IDS:
            logger.warning(f"Invalid assignee_id {classification.assignee_id}, routing to triage")
            classification.assignee_id = "u_triage"
            classification.category = "triage"
            classification.confidence = 0.3
        
        if classification.category not in VALID_CATEGORIES:
            logger.warning(f"Invalid category {classification.category}, setting to triage")
            classification.category = "triage"
        
        if classification.priority not in VALID_PRIORITIES:
            logger.warning(f"Invalid priority {classification.priority}, setting to medium")
            classification.priority = "medium"
        
        # Validate deal value
        if classification.deal_value_inr is not None:
            if not isinstance(classification.deal_value_inr, int) or classification.deal_value_inr < 0:
                logger.warning(f"Invalid deal_value_inr {classification.deal_value_inr}, setting to None")
                classification.deal_value_inr = None
        
        # Validate deadline format
        if classification.deadline is not None:
            try:
                datetime.strptime(classification.deadline, "%Y-%m-%d")
            except ValueError:
                logger.warning(f"Invalid deadline format {classification.deadline}, setting to None")
                classification.deadline = None
        
        return classification
    
    def _validate_routing_rules(self, classification: ClassificationResult) -> ClassificationResult:
        """Apply routing rule validation and corrections."""
        # If not a task, don't assign to anyone
        if not classification.is_task:
            classification.assignee_id = "u_triage"
            classification.category = "triage"
            return classification
        
        # Low confidence should route to triage
        if classification.confidence < 0.6:
            logger.info(f"Low confidence {classification.confidence}, routing to triage")
            classification.assignee_id = "u_triage"
            classification.category = "triage"
            return classification
        
        # Validate assignee/category combinations follow routing rules
        # Aarti: enterprise_rfp
        if classification.assignee_id == "u_aarti" and classification.category not in ["enterprise_rfp", "triage"]:
            logger.warning(f"u_aarti assigned to {classification.category}, correcting to enterprise_rfp")
            classification.category = "enterprise_rfp"
        
        # Rohit: smb_enquiry
        if classification.assignee_id == "u_rohit" and classification.category not in ["smb_enquiry", "triage"]:
            logger.warning(f"u_rohit assigned to {classification.category}, correcting to smb_enquiry")
            classification.category = "smb_enquiry"
        
        # Meera: marketing
        if classification.assignee_id == "u_meera" and classification.category not in ["marketing", "triage"]:
            logger.warning(f"u_meera assigned to {classification.category}, correcting to marketing")
            classification.category = "marketing"
        
        # Karan: alliances
        if classification.assignee_id == "u_karan" and classification.category not in ["alliances", "triage"]:
            logger.warning(f"u_karan assigned to {classification.category}, correcting to alliances")
            classification.category = "alliances"
        
        # Divya: finance
        if classification.assignee_id == "u_divya" and classification.category not in ["finance", "triage"]:
            logger.warning(f"u_divya assigned to {classification.category}, correcting to finance")
            classification.category = "finance"
        
        # Deal value routing check
        if classification.deal_value_inr is not None:
            if classification.deal_value_inr > 1000000 and classification.assignee_id == "u_rohit":
                logger.info(f"Deal value ₹{classification.deal_value_inr} > ₹10L, reassigning from u_rohit to u_aarti")
                classification.assignee_id = "u_aarti"
                classification.category = "enterprise_rfp"
            elif classification.deal_value_inr <= 1000000 and classification.assignee_id == "u_aarti":
                logger.info(f"Deal value ₹{classification.deal_value_inr} <= ₹10L, reassigning from u_aarti to u_rohit")
                classification.assignee_id = "u_rohit"
                classification.category = "smb_enquiry"
        
        return classification
    
    def classify_email(self, email: EmailInput) -> ClassificationResult:
        """Classify an email with full validation and routing safeguards."""
        if not self.gemini.is_available():
            raise ValueError("Gemini classifier not available - GEMINI_API_KEY not configured")
        
        # Get classification from Gemini
        classification = self.gemini.classify(email)
        
        # Apply validation
        classification = self._validate_classification(classification)
        
        # Apply routing rules
        classification = self._validate_routing_rules(classification)
        
        logger.info(f"Final classification for email {email.email_id}: assignee={classification.assignee_id}, category={classification.category}, is_task={classification.is_task}, confidence={classification.confidence}")
        
        return classification
    
    def classify_email_mock(self, email: EmailInput, mock_result: dict) -> ClassificationResult:
        """Classify an email using a mock result (for testing)."""
        # Directly work with dict to avoid Pydantic validation issues during testing
        # This allows us to test the validation layer with invalid inputs
        classification_dict = {
            "category": mock_result.get("category") or "triage",
            "assignee_id": mock_result.get("assignee_id") or "u_triage",
            "priority": mock_result.get("priority") or "medium",
            "company_name": mock_result.get("company_name"),
            "deal_value_inr": mock_result.get("deal_value_inr"),
            "deadline": mock_result.get("deadline"),
            "confidence": mock_result.get("confidence", 0.5),
            "is_task": mock_result.get("is_task", True),
            "reason": mock_result.get("reason", "Mock classification")
        }
        
        # Apply validation (this will correct invalid values)
        classification = self._validate_classification_dict(classification_dict)
        
        # Apply routing rules
        classification = self._validate_routing_rules(classification)
        
        return classification
    
    def _validate_classification_dict(self, classification_dict: dict) -> ClassificationResult:
        """Validate classification from dict (for testing with invalid inputs)."""
        # Clamp confidence
        classification_dict["confidence"] = max(0.0, min(1.0, classification_dict.get("confidence", 0.5)))
        
        # Validate and correct enum values
        if classification_dict.get("assignee_id") not in VALID_ASSIGNEE_IDS:
            logger.warning(f"Invalid assignee_id {classification_dict.get('assignee_id')}, routing to triage")
            classification_dict["assignee_id"] = "u_triage"
            classification_dict["category"] = "triage"
        
        if classification_dict.get("category") not in VALID_CATEGORIES:
            logger.warning(f"Invalid category {classification_dict.get('category')}, setting to triage")
            classification_dict["category"] = "triage"
        
        if classification_dict.get("priority") not in VALID_PRIORITIES:
            logger.warning(f"Invalid priority {classification_dict.get('priority')}, setting to medium")
            classification_dict["priority"] = "medium"
        
        # Validate deal value
        if classification_dict.get("deal_value_inr") is not None:
            if not isinstance(classification_dict["deal_value_inr"], int) or classification_dict["deal_value_inr"] < 0:
                logger.warning(f"Invalid deal_value_inr {classification_dict['deal_value_inr']}, setting to None")
                classification_dict["deal_value_inr"] = None
        
        # Validate deadline format
        if classification_dict.get("deadline") is not None:
            try:
                datetime.strptime(classification_dict["deadline"], "%Y-%m-%d")
            except ValueError:
                logger.warning(f"Invalid deadline format {classification_dict['deadline']}, setting to None")
                classification_dict["deadline"] = None
        
        return ClassificationResult(**classification_dict)
    
    def is_available(self) -> bool:
        """Check if classification service is available."""
        return self.gemini.is_available()
