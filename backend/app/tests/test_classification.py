import pytest
from app.schemas.email import EmailInput
from app.services.classification_service import ClassificationService


class TestClassificationService:
    """Test suite for email classification service with mocked Gemini responses."""
    
    def setup_method(self):
        """Set up classification service for testing."""
        self.service = ClassificationService()
    
    def test_enterprise_rfp_above_10_lakh_to_aarti(self):
        """Test Enterprise RFP > ₹10 lakh → u_aarti."""
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
        
        mock_result = {
            "category": "enterprise_rfp",
            "assignee_id": "u_aarti",
            "priority": "high",
            "company_name": "Meridian Steel",
            "deal_value_inr": 1500000,
            "deadline": "2026-09-15",
            "confidence": 0.85,
            "is_task": True,
            "reason": "Enterprise RFP with deal value above threshold"
        }
        
        result = self.service.classify_email_mock(email, mock_result)
        
        assert result.category == "enterprise_rfp"
        assert result.assignee_id == "u_aarti"
        assert result.deal_value_inr == 1500000
        assert result.is_task is True
    
    def test_rfi_to_aarti(self):
        """Test RFI → u_aarti."""
        email = EmailInput(
            email_id="em_002",
            thread_id="th_002",
            from_name="Jane Doe",
            from_email="jane@techcorp.com",
            to="sales@aluminix.com",
            subject="Request for Information - AI Platform",
            body="We need information about your AI platform capabilities.",
            received_at=None
        )
        
        mock_result = {
            "category": "enterprise_rfp",
            "assignee_id": "u_aarti",
            "priority": "high",
            "company_name": "TechCorp",
            "deal_value_inr": None,
            "deadline": None,
            "confidence": 0.80,
            "is_task": True,
            "reason": "RFI for enterprise solution"
        }
        
        result = self.service.classify_email_mock(email, mock_result)
        
        assert result.category == "enterprise_rfp"
        assert result.assignee_id == "u_aarti"
        assert result.is_task is True
    
    def test_tender_to_aarti(self):
        """Test Tender → u_aarti."""
        email = EmailInput(
            email_id="em_003",
            thread_id="th_003",
            from_name="Government Office",
            from_email="procurement@gov.in",
            to="sales@aluminix.com",
            subject="Tender Notice - Document Management System",
            body="Government tender for DMS implementation.",
            received_at=None
        )
        
        mock_result = {
            "category": "enterprise_rfp",
            "assignee_id": "u_aarti",
            "priority": "high",
            "company_name": "Government Office",
            "deal_value_inr": 5000000,
            "deadline": "2026-10-01",
            "confidence": 0.90,
            "is_task": True,
            "reason": "Government tender for enterprise solution"
        }
        
        result = self.service.classify_email_mock(email, mock_result)
        
        assert result.category == "enterprise_rfp"
        assert result.assignee_id == "u_aarti"
        assert result.is_task is True
    
    def test_smb_enquiry_below_10_lakh_to_rohit(self):
        """Test SMB enquiry ≤ ₹10 lakh → u_rohit."""
        email = EmailInput(
            email_id="em_004",
            thread_id="th_004",
            from_name="Small Business Owner",
            from_email="owner@startup.com",
            to="sales@aluminix.com",
            subject="Enquiry about basic plan",
            body="We need a basic plan for our startup. Budget is ₹5,00,000.",
            received_at=None
        )
        
        mock_result = {
            "category": "smb_enquiry",
            "assignee_id": "u_rohit",
            "priority": "medium",
            "company_name": "Startup Inc",
            "deal_value_inr": 500000,
            "deadline": None,
            "confidence": 0.85,
            "is_task": True,
            "reason": "SMB enquiry with deal value below threshold"
        }
        
        result = self.service.classify_email_mock(email, mock_result)
        
        assert result.category == "smb_enquiry"
        assert result.assignee_id == "u_rohit"
        assert result.deal_value_inr == 500000
        assert result.is_task is True
    
    def test_demo_request_to_rohit(self):
        """Test Demo request → u_rohit."""
        email = EmailInput(
            email_id="em_005",
            thread_id="th_005",
            from_name="Product Manager",
            from_email="pm@company.com",
            to="sales@aluminix.com",
            subject="Request for Product Demo",
            body="We would like to schedule a demo of your product.",
            received_at=None
        )
        
        mock_result = {
            "category": "smb_enquiry",
            "assignee_id": "u_rohit",
            "priority": "medium",
            "company_name": "Company",
            "deal_value_inr": None,
            "deadline": None,
            "confidence": 0.80,
            "is_task": True,
            "reason": "Demo request for SMB"
        }
        
        result = self.service.classify_email_mock(email, mock_result)
        
        assert result.category == "smb_enquiry"
        assert result.assignee_id == "u_rohit"
        assert result.is_task is True
    
    def test_webinar_sponsorship_to_meera(self):
        """Test Webinar/sponsorship → u_meera."""
        email = EmailInput(
            email_id="em_006",
            thread_id="th_006",
            from_name="Event Organizer",
            from_email="events@techsummit.com",
            to="marketing@aluminix.com",
            subject="Sponsorship Opportunity - Tech Summit 2026",
            body="We would like to discuss sponsorship for our upcoming tech summit.",
            received_at=None
        )
        
        mock_result = {
            "category": "marketing",
            "assignee_id": "u_meera",
            "priority": "medium",
            "company_name": "Tech Summit",
            "deal_value_inr": None,
            "deadline": "2026-11-01",
            "confidence": 0.85,
            "is_task": True,
            "reason": "Event sponsorship opportunity"
        }
        
        result = self.service.classify_email_mock(email, mock_result)
        
        assert result.category == "marketing"
        assert result.assignee_id == "u_meera"
        assert result.is_task is True
    
    def test_reseller_proposal_to_karan(self):
        """Test Reseller proposal → u_karan."""
        email = EmailInput(
            email_id="em_007",
            thread_id="th_007",
            from_name="Channel Partner",
            from_email="partner@reseller.com",
            to="alliances@aluminix.com",
            subject="Reseller Partnership Proposal",
            body="We are interested in becoming a reseller for your products.",
            received_at=None
        )
        
        mock_result = {
            "category": "alliances",
            "assignee_id": "u_karan",
            "priority": "medium",
            "company_name": "Reseller Corp",
            "deal_value_inr": None,
            "deadline": None,
            "confidence": 0.80,
            "is_task": True,
            "reason": "Reseller partnership proposal"
        }
        
        result = self.service.classify_email_mock(email, mock_result)
        
        assert result.category == "alliances"
        assert result.assignee_id == "u_karan"
        assert result.is_task is True
    
    def test_technology_integration_to_karan(self):
        """Test Technology integration → u_karan."""
        email = EmailInput(
            email_id="em_008",
            thread_id="th_008",
            from_name="CTO",
            from_email="cto@techpartner.com",
            to="alliances@aluminix.com",
            subject="Technology Integration Opportunity",
            body="We would like to integrate your AI platform with our existing systems.",
            received_at=None
        )
        
        mock_result = {
            "category": "alliances",
            "assignee_id": "u_karan",
            "priority": "high",
            "company_name": "TechPartner",
            "deal_value_inr": None,
            "deadline": "2026-12-01",
            "confidence": 0.85,
            "is_task": True,
            "reason": "Technology integration partnership"
        }
        
        result = self.service.classify_email_mock(email, mock_result)
        
        assert result.category == "alliances"
        assert result.assignee_id == "u_karan"
        assert result.is_task is True
    
    def test_invoice_to_divya(self):
        """Test Invoice → u_divya."""
        email = EmailInput(
            email_id="em_009",
            thread_id="th_009",
            from_name="Accounts Payable",
            from_email="ap@client.com",
            to="finance@aluminix.com",
            subject="Invoice #INV-2026-001",
            body="Please find attached invoice for services rendered.",
            received_at=None
        )
        
        mock_result = {
            "category": "finance",
            "assignee_id": "u_divya",
            "priority": "medium",
            "company_name": "Client Corp",
            "deal_value_inr": 250000,
            "deadline": "2026-08-30",
            "confidence": 0.90,
            "is_task": True,
            "reason": "Invoice payment request"
        }
        
        result = self.service.classify_email_mock(email, mock_result)
        
        assert result.category == "finance"
        assert result.assignee_id == "u_divya"
        assert result.is_task is True
    
    def test_gst_payment_to_divya(self):
        """Test GST/payment/PO → u_divya."""
        email = EmailInput(
            email_id="em_010",
            thread_id="th_010",
            from_name="Finance Team",
            from_email="finance@vendor.com",
            to="finance@aluminix.com",
            subject="GST Payment and Purchase Order",
            body="Regarding GST payment and PO processing.",
            received_at=None
        )
        
        mock_result = {
            "category": "finance",
            "assignee_id": "u_divya",
            "priority": "high",
            "company_name": "Vendor Inc",
            "deal_value_inr": None,
            "deadline": "2026-08-20",
            "confidence": 0.85,
            "is_task": True,
            "reason": "GST and payment processing"
        }
        
        result = self.service.classify_email_mock(email, mock_result)
        
        assert result.category == "finance"
        assert result.assignee_id == "u_divya"
        assert result.is_task is True
    
    def test_ambiguous_email_to_triage(self):
        """Test Ambiguous email → u_triage."""
        email = EmailInput(
            email_id="em_011",
            thread_id="th_011",
            from_name="Unknown Sender",
            from_email="unknown@email.com",
            to="info@aluminix.com",
            subject="Question",
            body="I have a question about your company.",
            received_at=None
        )
        
        mock_result = {
            "category": "triage",
            "assignee_id": "u_triage",
            "priority": "low",
            "company_name": None,
            "deal_value_inr": None,
            "deadline": None,
            "confidence": 0.40,
            "is_task": True,
            "reason": "Insufficient information to classify"
        }
        
        result = self.service.classify_email_mock(email, mock_result)
        
        assert result.category == "triage"
        assert result.assignee_id == "u_triage"
        assert result.is_task is True
    
    def test_out_of_office_is_task_false(self):
        """Test Out-of-office → is_task=false."""
        email = EmailInput(
            email_id="em_012",
            thread_id="th_012",
            from_name="Auto Reply",
            from_email="user@company.com",
            to="sales@aluminix.com",
            subject="Out of Office",
            body="I will be out of office until August 14.",
            received_at=None
        )
        
        mock_result = {
            "category": "triage",
            "assignee_id": "u_triage",
            "priority": "low",
            "company_name": None,
            "deal_value_inr": None,
            "deadline": None,
            "confidence": 0.95,
            "is_task": False,
            "reason": "Out of office autoreply"
        }
        
        result = self.service.classify_email_mock(email, mock_result)
        
        assert result.is_task is False
        assert result.assignee_id == "u_triage"
    
    def test_newsletter_is_task_false(self):
        """Test Newsletter → is_task=false."""
        email = EmailInput(
            email_id="em_013",
            thread_id="th_013",
            from_name="Newsletter",
            from_email="news@marketing.com",
            to="sales@aluminix.com",
            subject="B2B Growth Weekly — Issue #212",
            body="Weekly newsletter about B2B growth strategies.",
            received_at=None
        )
        
        mock_result = {
            "category": "triage",
            "assignee_id": "u_triage",
            "priority": "low",
            "company_name": None,
            "deal_value_inr": None,
            "deadline": None,
            "confidence": 0.90,
            "is_task": False,
            "reason": "Newsletter - not actionable"
        }
        
        result = self.service.classify_email_mock(email, mock_result)
        
        assert result.is_task is False
        assert result.assignee_id == "u_triage"
    
    def test_vendor_seo_spam_is_task_false(self):
        """Test Vendor SEO spam → is_task=false."""
        email = EmailInput(
            email_id="em_014",
            thread_id="th_014",
            from_name="SEO Agency",
            from_email="sales@seoagency.com",
            to="sales@aluminix.com",
            subject="We can improve your SEO ranking",
            body="We can improve your SEO ranking and webinar marketing. Book a call.",
            received_at=None
        )
        
        mock_result = {
            "category": "triage",
            "assignee_id": "u_triage",
            "priority": "low",
            "company_name": None,
            "deal_value_inr": None,
            "deadline": None,
            "confidence": 0.85,
            "is_task": False,
            "reason": "Unsolicited vendor spam"
        }
        
        result = self.service.classify_email_mock(email, mock_result)
        
        assert result.is_task is False
        assert result.assignee_id == "u_triage"
    
    def test_invalid_gemini_enum_safely_handled(self):
        """Test Invalid Gemini enum → safely handled."""
        email = EmailInput(
            email_id="em_015",
            thread_id="th_015",
            from_name="Test User",
            from_email="test@test.com",
            to="sales@aluminix.com",
            subject="Test",
            body="Test email",
            received_at=None
        )
        
        # Invalid assignee_id
        mock_result = {
            "category": "enterprise_rfp",
            "assignee_id": "invalid_user",
            "priority": "high",
            "company_name": None,
            "deal_value_inr": None,
            "deadline": None,
            "confidence": 0.75,
            "is_task": True,
            "reason": "Test"
        }
        
        result = self.service.classify_email_mock(email, mock_result)
        
        # Should be corrected to triage
        assert result.assignee_id == "u_triage"
        assert result.category == "triage"
    
    def test_low_confidence_to_triage(self):
        """Test Low-confidence classification → u_triage."""
        email = EmailInput(
            email_id="em_016",
            thread_id="th_016",
            from_name="Uncertain Sender",
            from_email="uncertain@email.com",
            to="sales@aluminix.com",
            subject="Uncertain inquiry",
            body="Maybe interested in your products, not sure yet.",
            received_at=None
        )
        
        mock_result = {
            "category": "smb_enquiry",
            "assignee_id": "u_rohit",
            "priority": "medium",
            "company_name": None,
            "deal_value_inr": None,
            "deadline": None,
            "confidence": 0.50,
            "is_task": True,
            "reason": "Low confidence classification"
        }
        
        result = self.service.classify_email_mock(email, mock_result)
        
        # Low confidence should route to triage
        assert result.assignee_id == "u_triage"
        assert result.category == "triage"
    
    def test_confidence_clamping(self):
        """Test confidence is clamped to valid range."""
        email = EmailInput(
            email_id="em_017",
            thread_id="th_017",
            from_name="Test User",
            from_email="test@test.com",
            to="sales@aluminix.com",
            subject="Test",
            body="Test",
            received_at=None
        )
        
        # Test confidence above 1.0
        mock_result = {
            "category": "smb_enquiry",
            "assignee_id": "u_rohit",
            "priority": "medium",
            "company_name": None,
            "deal_value_inr": None,
            "deadline": None,
            "confidence": 1.5,
            "is_task": True,
            "reason": "Test"
        }
        
        result = self.service.classify_email_mock(email, mock_result)
        assert result.confidence == 1.0
        
        # Test confidence below 0.0
        mock_result["confidence"] = -0.5
        result = self.service.classify_email_mock(email, mock_result)
        assert result.confidence == 0.0
    
    def test_invalid_deadline_format_handled(self):
        """Test invalid deadline format is handled."""
        email = EmailInput(
            email_id="em_018",
            thread_id="th_018",
            from_name="Test User",
            from_email="test@test.com",
            to="sales@aluminix.com",
            subject="Test",
            body="Test",
            received_at=None
        )
        
        mock_result = {
            "category": "smb_enquiry",
            "assignee_id": "u_rohit",
            "priority": "medium",
            "company_name": None,
            "deal_value_inr": None,
            "deadline": "invalid-date",
            "confidence": 0.80,
            "is_task": True,
            "reason": "Test"
        }
        
        result = self.service.classify_email_mock(email, mock_result)
        assert result.deadline is None
    
    def test_invalid_deal_value_handled(self):
        """Test invalid deal value is handled."""
        email = EmailInput(
            email_id="em_019",
            thread_id="th_019",
            from_name="Test User",
            from_email="test@test.com",
            to="sales@aluminix.com",
            subject="Test",
            body="Test",
            received_at=None
        )
        
        # Test negative deal value
        mock_result = {
            "category": "smb_enquiry",
            "assignee_id": "u_rohit",
            "priority": "medium",
            "company_name": None,
            "deal_value_inr": -100000,
            "deadline": None,
            "confidence": 0.80,
            "is_task": True,
            "reason": "Test"
        }
        
        result = self.service.classify_email_mock(email, mock_result)
        assert result.deal_value_inr is None
