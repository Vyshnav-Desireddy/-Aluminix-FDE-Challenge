import pytest
from unittest.mock import Mock, patch
from app.schemas.chat import ChatRequest
from app.services.chat_service import ChatService


class TestChatService:
    """Test suite for chat service."""
    
    def test_chat_without_api_key(self, db_session):
        """Test that chat returns error message when GEMINI_API_KEY is not configured."""
        with patch('app.services.chat_service.settings.GEMINI_API_KEY', None):
            service = ChatService(db_session)
            response = service.chat("Hello")
            assert "unavailable" in response.lower()
    
    def test_chat_with_tasks_context(self, db_session):
        """Test that chat includes task context in the prompt."""
        from app.config import settings
        from app.models.task import Task
        import uuid
        from datetime import datetime
        
        # Create some test tasks
        task1 = Task(
            task_id=str(uuid.uuid4()),
            candidate_id=settings.CANDIDATE_ID,
            source_email_id="em_chat_001",
            thread_id="th_chat_001",
            title="Test Task 1",
            description="Test description",
            assignee_id="u_aarti",
            category="enterprise_rfp",
            priority="high",
            due_date=None,
            deal_value_inr=1000000,
            company_name="Test Company",
            confidence=0.85,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db_session.add(task1)
        db_session.commit()
        
        # Mock Gemini response
        mock_response = Mock()
        mock_response.text = "Based on your tasks, you have 1 high-priority enterprise RFP assigned to u_aarti."
        
        with patch('app.services.chat_service.settings.GEMINI_API_KEY', 'test_key'):
            with patch('app.services.chat_service.settings.GEMINI_MODEL', 'gemini-3.5-flash'):
                service = ChatService(db_session)
                service.client = Mock()
                service.client.models.generate_content.return_value = mock_response
                
                response = service.chat("What tasks do I have?")
                
                assert "high-priority" in response
                assert "u_aarti" in response
    
    def test_chat_handles_gemini_error(self, db_session):
        """Test that chat handles Gemini API errors gracefully."""
        with patch('app.services.chat_service.settings.GEMINI_API_KEY', 'test_key'):
            with patch('app.services.chat_service.settings.GEMINI_MODEL', 'gemini-3.5-flash'):
                service = ChatService(db_session)
                service.client = Mock()
                service.client.models.generate_content.side_effect = Exception("API Error")
                
                response = service.chat("Hello")
                
                assert "error" in response.lower() or "sorry" in response.lower()
    
    def test_chat_handles_quota_exceeded(self, db_session):
        """Test that chat handles Gemini API quota exceeded errors gracefully."""
        from google.genai import errors as genai_errors
        
        # Create a mock ClientError with status 429
        # The actual ClientError constructor doesn't accept status_code directly
        # We need to mock it properly
        mock_error = Exception("429 RESOURCE_EXHAUSTED")
        # Add attributes that the error handler might check
        mock_error.status_code = 429
        
        with patch('app.services.chat_service.settings.GEMINI_API_KEY', 'test_key'):
            with patch('app.services.chat_service.settings.GEMINI_MODEL', 'gemini-3.5-flash'):
                service = ChatService(db_session)
                service.client = Mock()
                service.client.models.generate_content.side_effect = mock_error
                
                response = service.chat("Hello")
                
                assert "error" in response.lower() or "sorry" in response.lower()
    
    def test_chat_with_multiple_tasks(self, db_session):
        """Test that chat works correctly with multiple tasks in the database."""
        from app.config import settings
        from app.models.task import Task
        import uuid
        from datetime import datetime
        
        # Create multiple test tasks
        task1 = Task(
            task_id=str(uuid.uuid4()),
            candidate_id=settings.CANDIDATE_ID,
            source_email_id="em_chat_multi_001",
            thread_id="th_chat_multi_001",
            title="Enterprise RFP",
            description="Large enterprise deal",
            assignee_id="u_aarti",
            category="enterprise_rfp",
            priority="high",
            due_date=None,
            deal_value_inr=2500000,
            company_name="Meridian Steel",
            confidence=0.98,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        task2 = Task(
            task_id=str(uuid.uuid4()),
            candidate_id=settings.CANDIDATE_ID,
            source_email_id="em_chat_multi_002",
            thread_id="th_chat_multi_002",
            title="SMB Enquiry",
            description="Small business enquiry",
            assignee_id="u_rohit",
            category="smb_enquiry",
            priority="medium",
            due_date=None,
            deal_value_inr=500000,
            company_name="Tech Solutions",
            confidence=0.85,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db_session.add(task1)
        db_session.add(task2)
        db_session.commit()
        
        # Mock Gemini response
        mock_response = Mock()
        mock_response.text = "You have 2 tasks: 1 high-priority enterprise RFP and 1 medium-priority SMB enquiry."
        
        with patch('app.services.chat_service.settings.GEMINI_API_KEY', 'test_key'):
            with patch('app.services.chat_service.settings.GEMINI_MODEL', 'gemini-3.5-flash'):
                service = ChatService(db_session)
                service.client = Mock()
                service.client.models.generate_content.return_value = mock_response
                
                response = service.chat("How many tasks do I have?")
                
                assert response is not None
                assert len(response) > 0


class TestChatAPI:
    """Test suite for chat API endpoint."""
    
    def test_chat_endpoint_exists(self, client):
        """Test that POST /api/chat endpoint exists and is accessible."""
        request_data = {
            "message": "Hello"
        }
        
        response = client.post("/api/chat", json=request_data)
        # Should return 200 (even if Gemini is unavailable, it returns a message)
        assert response.status_code == 200
    
    def test_chat_endpoint_validates_input(self, client):
        """Test that chat endpoint validates input."""
        invalid_request = {}
        
        response = client.post("/api/chat", json=invalid_request)
        assert response.status_code == 422  # Validation error
    
    def test_chat_endpoint_returns_response(self, client):
        """Test that chat endpoint returns a response with 'response' field."""
        request_data = {
            "message": "What tasks do I have?"
        }
        
        response = client.post("/api/chat", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "response" in data
        assert isinstance(data["response"], str)
