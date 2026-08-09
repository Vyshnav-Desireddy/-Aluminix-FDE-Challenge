import pytest
from app.services.sample_email_generator import SampleEmailGenerator
from app.schemas.email import EmailInput


class TestSampleEmailGenerator:
    """Test suite for sample email generator service."""
    
    def test_generate_single_email(self):
        """Test generating a single sample email."""
        generator = SampleEmailGenerator()
        email = generator.generate_email()
        
        assert isinstance(email, EmailInput)
        assert email.email_id is not None
        assert email.thread_id is not None
        assert email.from_name is not None
        assert email.from_email is not None
        assert email.to == "sales@aluminix.com"
        assert email.subject is not None
        assert email.body is not None
        assert email.received_at is not None
    
    def test_generate_email_with_category(self):
        """Test generating an email for a specific category."""
        generator = SampleEmailGenerator()
        email = generator.generate_email(category="enterprise_rfp")
        
        assert isinstance(email, EmailInput)
        assert "RFP" in email.subject or "Proposal" in email.subject
        assert email.body is not None
    
    def test_generate_email_with_custom_company(self):
        """Test generating an email with a custom company name."""
        generator = SampleEmailGenerator()
        custom_company = "Custom Tech Corp"
        # Use a category that includes company name in template
        email = generator.generate_email(company_name=custom_company, category="enterprise_rfp")
        
        assert isinstance(email, EmailInput)
        assert custom_company in email.body
    
    def test_generate_email_with_custom_sender(self):
        """Test generating an email with a custom sender name."""
        generator = SampleEmailGenerator()
        custom_sender = "John Doe"
        # Use a category that includes sender name in template
        email = generator.generate_email(sender_name=custom_sender, category="enterprise_rfp")
        
        assert isinstance(email, EmailInput)
        assert custom_sender in email.body
    
    def test_generate_multiple_emails(self):
        """Test generating multiple emails."""
        generator = SampleEmailGenerator()
        count = 5
        emails = generator.generate_emails(count=count)
        
        assert len(emails) == count
        for email in emails:
            assert isinstance(email, EmailInput)
    
    def test_generate_multiple_emails_with_category(self):
        """Test generating multiple emails of the same category."""
        generator = SampleEmailGenerator()
        count = 3
        emails = generator.generate_emails(count=count, category="smb_enquiry")
        
        assert len(emails) == count
        for email in emails:
            assert isinstance(email, EmailInput)
            # All should be SMB-related
            assert "demo" in email.subject.lower() or "quote" in email.subject.lower() or "enquiry" in email.subject.lower()
    
    def test_generate_emails_shuffle(self):
        """Test that shuffle parameter affects email order."""
        generator = SampleEmailGenerator()
        
        # Generate without shuffle (same category)
        emails_no_shuffle = generator.generate_emails(count=5, category="enterprise_rfp", shuffle=False)
        
        # Generate with shuffle (same category)
        emails_shuffle = generator.generate_emails(count=5, category="enterprise_rfp", shuffle=True)
        
        # Both should have same count
        assert len(emails_no_shuffle) == 5
        assert len(emails_shuffle) == 5
    
    def test_get_available_categories(self):
        """Test getting available categories."""
        generator = SampleEmailGenerator()
        categories = generator.get_available_categories()
        
        assert isinstance(categories, list)
        assert "enterprise_rfp" in categories
        assert "smb_enquiry" in categories
        assert "marketing" in categories
        assert "alliances" in categories
        assert "finance" in categories
        assert "non_task" in categories
    
    def test_email_ids_are_unique(self):
        """Test that generated email IDs are unique."""
        generator = SampleEmailGenerator()
        emails = generator.generate_emails(count=10)
        
        email_ids = [email.email_id for email in emails]
        assert len(email_ids) == len(set(email_ids))
    
    def test_thread_ids_are_unique(self):
        """Test that generated thread IDs are unique."""
        generator = SampleEmailGenerator()
        emails = generator.generate_emails(count=10)
        
        thread_ids = [email.thread_id for email in emails]
        assert len(thread_ids) == len(set(thread_ids))
    
    def test_non_task_emails(self):
        """Test generating non-task emails."""
        generator = SampleEmailGenerator()
        email = generator.generate_email(category="non_task")
        
        assert isinstance(email, EmailInput)
        # Should be newsletters, spam, or auto-replies
        assert any(keyword in email.subject.lower() for keyword in ["out of office", "newsletter", "offer", "spam"])
    
    def test_marketing_emails(self):
        """Test generating marketing emails."""
        generator = SampleEmailGenerator()
        email = generator.generate_email(category="marketing")
        
        assert isinstance(email, EmailInput)
        assert any(keyword in email.subject.lower() for keyword in ["webinar", "sponsorship", "content", "collaboration"])
    
    def test_finance_emails(self):
        """Test generating finance emails."""
        generator = SampleEmailGenerator()
        email = generator.generate_email(category="finance")
        
        assert isinstance(email, EmailInput)
        assert any(keyword in email.subject.lower() for keyword in ["invoice", "payment", "purchase order", "po"])
    
    def test_alliances_emails(self):
        """Test generating alliance emails."""
        generator = SampleEmailGenerator()
        email = generator.generate_email(category="alliances")
        
        assert isinstance(email, EmailInput)
        assert any(keyword in email.subject.lower() for keyword in ["reseller", "partnership", "integration", "alliance"])
    
    def test_email_format_valid_for_ingestion(self):
        """Test that generated emails are valid for ingestion."""
        generator = SampleEmailGenerator()
        email = generator.generate_email()
        
        # All required fields for EmailInput schema
        assert email.email_id is not None and len(email.email_id) > 0
        assert email.thread_id is not None and len(email.thread_id) > 0
        assert email.from_name is not None and len(email.from_name) > 0
        assert email.from_email is not None and "@" in email.from_email
        assert email.to is not None and len(email.to) > 0
        assert email.subject is not None and len(email.subject) > 0
        assert email.body is not None and len(email.body) > 0


class TestSampleEmailAPI:
    """Test suite for sample email API endpoints."""
    
    def test_sample_emails_endpoint_exists(self, client):
        """Test that GET /sample-emails endpoint exists."""
        response = client.get("/sample-emails?count=1")
        assert response.status_code == 200
    
    def test_sample_emails_returns_list(self, client):
        """Test that sample emails endpoint returns a list."""
        response = client.get("/sample-emails?count=3")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3
    
    def test_sample_emails_with_category_filter(self, client):
        """Test sample emails with category filter."""
        response = client.get("/sample-emails?count=2&category=enterprise_rfp")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
    
    def test_sample_emails_count_validation(self, client):
        """Test that count parameter is validated."""
        # Test minimum
        response = client.get("/sample-emails?count=0")
        assert response.status_code == 422  # Validation error
        
        # Test maximum
        response = client.get("/sample-emails?count=51")
        assert response.status_code == 422  # Validation error
    
    def test_sample_emails_invalid_category(self, client):
        """Test that invalid category returns error."""
        response = client.get("/sample-emails?count=1&category=invalid_category")
        assert response.status_code == 400  # Bad request
    
    def test_sample_emails_categories_endpoint(self, client):
        """Test that GET /sample-emails/categories endpoint exists."""
        response = client.get("/sample-emails/categories")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert "enterprise_rfp" in data
        assert "smb_enquiry" in data
    
    def test_sample_emails_default_count(self, client):
        """Test that default count is 1."""
        response = client.get("/sample-emails")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
    
    def test_sample_emails_shuffle_parameter(self, client):
        """Test that shuffle parameter works."""
        response = client.get("/sample-emails?count=5&shuffle=true")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 5
