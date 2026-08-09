import pytest
from unittest.mock import Mock, patch
from app.schemas.email import EmailInput
from app.services.ingestion_service import IngestionService
from app.schemas.classification import ClassificationResult


class TestIngestionService:
    """Test suite for email ingestion service."""
    
    def setup_method(self):
        """Set up ingestion service for testing."""
        # Service will be created with db_session fixture
        pass
    
    def test_actionable_email_creates_task(self, db_session):
        """Test that an actionable email creates exactly one task."""
        service = IngestionService(db_session)
        
        email = EmailInput(
            email_id="em_001",
            thread_id="th_001",
            from_name="John Smith",
            from_email="john@meridiansteel.com",
            to="sales@aluminix.com",
            subject="RFP for Enterprise Document Management System",
            body="We are looking for an enterprise DMS solution. Budget is ₹15,00,000.",
            received_at=None
        )
        
        # Mock classification result for actionable email
        mock_classification = ClassificationResult(
            category="enterprise_rfp",
            assignee_id="u_aarti",
            priority="high",
            company_name="Meridian Steel",
            deal_value_inr=1500000,
            deadline="2026-09-15",
            confidence=0.85,
            is_task=True,
            reason="Enterprise RFP with deal value above threshold"
        )
        
        # Mock the classification service
        with patch.object(service.classification_service, 'classify_email', return_value=mock_classification):
            result = service.ingest_email(email)
        
        # Verify task was created
        assert result.status == "created"
        assert result.task is not None
        assert result.task.source_email_id == "em_001"
        assert result.task.assignee_id == "u_aarti"
        assert result.task.category == "enterprise_rfp"
        assert result.task.deal_value_inr == 1500000
    
    def test_non_task_email_does_not_create_task(self, db_session):
        """Test that a non-task email does not create a task."""
        service = IngestionService(db_session)
        
        email = EmailInput(
            email_id="em_002",
            thread_id="th_002",
            from_name="Auto Reply",
            from_email="noreply@company.com",
            to="sales@aluminix.com",
            subject="Out of Office",
            body="I am out of office until next week.",
            received_at=None
        )
        
        # Mock classification result for non-task email
        mock_classification = ClassificationResult(
            category="triage",
            assignee_id="u_triage",
            priority="low",
            company_name=None,
            deal_value_inr=None,
            deadline=None,
            confidence=0.95,
            is_task=False,
            reason="Out of office autoreply"
        )
        
        # Mock the classification service
        with patch.object(service.classification_service, 'classify_email', return_value=mock_classification):
            result = service.ingest_email(email)
        
        # Verify task was NOT created
        assert result.status == "ignored"
        assert result.task is None
        assert result.classification is not None
        assert result.classification.is_task is False
    
    def test_duplicate_email_returns_existing_task(self, db_session):
        """Test that a duplicate email does not create another task."""
        service = IngestionService(db_session)
        
        email = EmailInput(
            email_id="em_003",
            thread_id="th_003",
            from_name="Jane Doe",
            from_email="jane@company.com",
            to="sales@aluminix.com",
            subject="Duplicate Test",
            body="This is a test email.",
            received_at=None
        )
        
        # Mock classification result
        mock_classification = ClassificationResult(
            category="smb_enquiry",
            assignee_id="u_rohit",
            priority="medium",
            company_name="Test Company",
            deal_value_inr=500000,
            deadline="2026-10-01",
            confidence=0.75,
            is_task=True,
            reason="SMB enquiry"
        )
        
        # First ingestion
        with patch.object(service.classification_service, 'classify_email', return_value=mock_classification):
            result1 = service.ingest_email(email)
        
        assert result1.status == "created"
        first_task_id = result1.task.task_id
        
        # Second ingestion with same email_id
        with patch.object(service.classification_service, 'classify_email', return_value=mock_classification):
            result2 = service.ingest_email(email)
        
        assert result2.status == "duplicate"
        assert result2.task.task_id == first_task_id
    
    def test_candidate_id_from_configuration(self, db_session):
        """Test that candidate_id always comes from configuration."""
        service = IngestionService(db_session)
        
        email = EmailInput(
            email_id="em_004",
            thread_id="th_004",
            from_name="Test User",
            from_email="test@example.com",
            to="sales@aluminix.com",
            subject="Test",
            body="Test email",
            received_at=None
        )
        
        mock_classification = ClassificationResult(
            category="triage",
            assignee_id="u_triage",
            priority="medium",
            company_name=None,
            deal_value_inr=None,
            deadline=None,
            confidence=0.5,
            is_task=True,
            reason="Test"
        )
        
        with patch.object(service.classification_service, 'classify_email', return_value=mock_classification):
            result = service.ingest_email(email)
        
        # Verify candidate_id comes from configuration
        from app.config import settings
        assert result.task.candidate_id == settings.CANDIDATE_ID
    
    def test_classification_maps_to_task_fields(self, db_session):
        """Test that classification result maps correctly to Task fields."""
        service = IngestionService(db_session)
        
        email = EmailInput(
            email_id="em_005",
            thread_id="th_005",
            from_name="Test User",
            from_email="test@company.com",
            to="sales@aluminix.com",
            subject="Test Classification Mapping",
            body="Test email for field mapping",
            received_at=None
        )
        
        mock_classification = ClassificationResult(
            category="marketing",
            assignee_id="u_meera",
            priority="high",
            company_name="Marketing Corp",
            deal_value_inr=750000,
            deadline="2026-11-01",
            confidence=0.88,
            is_task=True,
            reason="Marketing collaboration"
        )
        
        with patch.object(service.classification_service, 'classify_email', return_value=mock_classification):
            result = service.ingest_email(email)
        
        # Verify all fields map correctly
        assert result.task.assignee_id == "u_meera"
        assert result.task.category == "marketing"
        assert result.task.priority == "high"
        assert result.task.company_name == "Marketing Corp"
        assert result.task.deal_value_inr == 750000
        assert result.task.confidence == 0.88
        assert result.task.thread_id == "th_005"
    
    def test_invalid_email_input_rejected(self, client):
        """Test that invalid email input is rejected."""
        invalid_email = {
            # Missing required fields
            "email_id": "em_006",
            "from_name": "Test"
            # Missing thread_id, from_email, to, subject, body
        }
        
        response = client.post("/ingest", json=invalid_email)
        assert response.status_code == 422  # Validation error


class TestIngestionAPI:
    """Test suite for ingestion API endpoint."""
    
    @patch('app.services.ingestion_service.ClassificationService')
    def test_ingest_endpoint_exists(self, mock_classification_class, client):
        """Test that POST /ingest endpoint exists and is accessible."""
        from app.schemas.classification import ClassificationResult
        
        # Mock the classification service to avoid real API calls
        mock_classification = Mock()
        mock_classification.classify_email.return_value = ClassificationResult(
            category="smb_enquiry",
            assignee_id="u_rohit",
            priority="medium",
            company_name="Test Company",
            deal_value_inr=500000,
            deadline="2026-10-01",
            confidence=0.75,
            is_task=True,
            reason="Test classification"
        )
        mock_classification_class.return_value = mock_classification
        
        email = {
            "email_id": "em_007",
            "thread_id": "th_007",
            "from_name": "Test User",
            "from_email": "test@example.com",
            "to": "sales@aluminix.com",
            "subject": "Test Endpoint",
            "body": "Test email"
        }
        
        response = client.post("/ingest", json=email)
        # Should return 200 or 201 (created) or 409 (conflict/duplicate)
        assert response.status_code in [200, 201]
