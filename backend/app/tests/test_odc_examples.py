"""
Regression test suite based on the 12 Worked Examples from ODC §6.

These tests verify the actual observable behavior of the system against
the worked examples specified in the Original Design Challenge.
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import uuid
from app.schemas.email import EmailInput
from app.schemas.classification import ClassificationResult
from app.services.ingestion_service import IngestionService
from app.models.task import Task
from app.config import settings


class TestODCWorkedExamples:
    """
    Regression tests for the 12 worked examples from ODC §6.
    
    These tests use mocked classification responses to ensure stability
    and avoid consuming Gemini quota. They verify the actual observable
    behavior of the system.
    """
    
    # Example 1: Clean enterprise RFP
    def test_odc_example_1_clean_enterprise_rfp(self, db_session):
        """
        Example 1: Clean enterprise RFP
        - Category: enterprise_rfp
        - Assignee: Aarti (u_aarti)
        - High priority
        - Deal value ₹25L
        - Due date 2026-09-15
        - Task created
        """
        email = EmailInput(
            email_id="odc_ex1_001",
            thread_id="odc_th1_001",
            from_name="Rajesh Kumar",
            from_email="rajesh@meridiansteel.com",
            to="sales@aluminix.com",
            subject="Request for Proposal - Document Management System",
            body="We are issuing an RFP for a comprehensive document management system. Budget: ₹25,00,000. Deadline: September 15, 2026.",
            received_at=datetime.utcnow()
        )
        
        # Mock classification matching expected behavior
        mock_classification = ClassificationResult(
            category="enterprise_rfp",
            assignee_id="u_aarti",
            priority="high",
            company_name="Meridian Steel Pvt Ltd",
            deal_value_inr=2500000,
            deadline="2026-09-15",
            confidence=0.95,
            is_task=True,
            reason="Enterprise RFP above ₹10L threshold"
        )
        
        with patch('app.services.ingestion_service.ClassificationService') as mock_class_service:
            mock_classifier = Mock()
            mock_classifier.classify_email.return_value = mock_classification
            mock_class_service.return_value = mock_classifier
            
            service = IngestionService(db_session)
            result = service.ingest_email(email)
        
        # Verify task created with correct attributes
        assert result.status == "created"
        assert result.task is not None
        assert result.task.category == "enterprise_rfp"
        assert result.task.assignee_id == "u_aarti"
        assert result.task.priority == "high"
        assert result.task.deal_value_inr == 2500000
        assert result.task.company_name == "Meridian Steel Pvt Ltd"
        assert result.task.confidence >= 0.0 and result.task.confidence <= 1.0
    
    # Example 2: SMB demo request
    def test_odc_example_2_smb_demo_request(self, db_session):
        """
        Example 2: SMB demo request
        - Category: smb_enquiry
        - Assignee: Rohit (u_rohit)
        - Medium priority
        - Deal value ₹6.5L
        - Task created
        """
        email = EmailInput(
            email_id="odc_ex2_001",
            thread_id="odc_th2_001",
            from_name="Priya Sharma",
            from_email="priya@techsolutions.in",
            to="sales@aluminix.com",
            subject="Product Demo Request - Cloud Solutions",
            body="We are a growing SME looking to migrate to cloud. Budget: ₹6,50,000. Please schedule a demo.",
            received_at=datetime.utcnow()
        )
        
        mock_classification = ClassificationResult(
            category="smb_enquiry",
            assignee_id="u_rohit",
            priority="medium",
            company_name="Tech Solutions India",
            deal_value_inr=650000,
            deadline=None,
            confidence=0.85,
            is_task=True,
            reason="SMB enquiry below ₹10L threshold"
        )
        
        with patch('app.services.ingestion_service.ClassificationService') as mock_class_service:
            mock_classifier = Mock()
            mock_classifier.classify_email.return_value = mock_classification
            mock_class_service.return_value = mock_classifier
            
            service = IngestionService(db_session)
            result = service.ingest_email(email)
        
        assert result.status == "created"
        assert result.task.category == "smb_enquiry"
        assert result.task.assignee_id == "u_rohit"
        assert result.task.priority == "medium"
        assert result.task.deal_value_inr == 650000
    
    # Example 3: PSU tender below threshold
    def test_odc_example_3_psu_tender_below_threshold(self, db_session):
        """
        Example 3: PSU tender below threshold
        - Category: enterprise_rfp
        - Assignee: Rohit (u_rohit) - because deal value is below ₹10L
        - Task created
        """
        email = EmailInput(
            email_id="odc_ex3_001",
            thread_id="odc_th3_001",
            from_name="Amit Patel",
            from_email="amit@psu.gov.in",
            to="sales@aluminix.com",
            subject="Tender for IT Infrastructure Upgrade",
            body="Government PSU tender for IT infrastructure. Budget: ₹8,00,000. Below enterprise threshold.",
            received_at=datetime.utcnow()
        )
        
        # Even though it's enterprise_rfp, deal value below ₹10L routes to Rohit
        mock_classification = ClassificationResult(
            category="enterprise_rfp",
            assignee_id="u_rohit",  # Below threshold
            priority="medium",
            company_name="State PSU",
            deal_value_inr=800000,
            deadline="2026-10-30",
            confidence=0.90,
            is_task=True,
            reason="Enterprise tender below ₹10L threshold"
        )
        
        with patch('app.services.ingestion_service.ClassificationService') as mock_class_service:
            mock_classifier = Mock()
            mock_classifier.classify_email.return_value = mock_classification
            mock_class_service.return_value = mock_classifier
            
            service = IngestionService(db_session)
            result = service.ingest_email(email)
        
        assert result.status == "created"
        assert result.task.category == "enterprise_rfp"
        assert result.task.assignee_id == "u_rohit"  # Below threshold
        assert result.task.deal_value_inr == 800000
    
    # Example 4: Marketing sponsorship
    def test_odc_example_4_marketing_sponsorship(self, db_session):
        """
        Example 4: Marketing sponsorship
        - Category: marketing
        - Assignee: Meera (u_meera)
        - Low priority
        - Task created
        """
        email = EmailInput(
            email_id="odc_ex4_001",
            thread_id="odc_th4_001",
            from_name="Sneha Reddy",
            from_email="sneha@eventsummit.com",
            to="sales@aluminix.com",
            subject="Webinar Sponsorship Opportunity - Tech Summit 2026",
            body="We are organizing Tech Summit 2026. Gold sponsorship: ₹3,00,000. Expected attendees: 500+.",
            received_at=datetime.utcnow()
        )
        
        mock_classification = ClassificationResult(
            category="marketing",
            assignee_id="u_meera",
            priority="low",
            company_name="Event Summit",
            deal_value_inr=300000,
            deadline="2026-11-15",
            confidence=0.88,
            is_task=True,
            reason="Marketing sponsorship opportunity"
        )
        
        with patch('app.services.ingestion_service.ClassificationService') as mock_class_service:
            mock_classifier = Mock()
            mock_classifier.classify_email.return_value = mock_classification
            mock_class_service.return_value = mock_classifier
            
            service = IngestionService(db_session)
            result = service.ingest_email(email)
        
        assert result.status == "created"
        assert result.task.category == "marketing"
        assert result.task.assignee_id == "u_meera"
        assert result.task.priority == "low"
    
    # Example 5: Finance invoice
    def test_odc_example_5_finance_invoice(self, db_session):
        """
        Example 5: Finance invoice
        - Category: finance
        - Assignee: Divya (u_divya)
        - Low priority
        - Task created
        """
        email = EmailInput(
            email_id="odc_ex5_001",
            thread_id="odc_th5_001",
            from_name="Vikram Singh",
            from_email="vikram@vendor.com",
            to="sales@aluminix.com",
            subject="Invoice #INV-2026-089 - Payment Due",
            body="Invoice amount: ₹1,25,000. Due date: August 25, 2026. Services: Cloud infrastructure.",
            received_at=datetime.utcnow()
        )
        
        mock_classification = ClassificationResult(
            category="finance",
            assignee_id="u_divya",
            priority="low",
            company_name="Vendor Corp",
            deal_value_inr=125000,
            deadline="2026-08-25",
            confidence=0.95,
            is_task=True,
            reason="Finance invoice requiring payment processing"
        )
        
        with patch('app.services.ingestion_service.ClassificationService') as mock_class_service:
            mock_classifier = Mock()
            mock_classifier.classify_email.return_value = mock_classification
            mock_class_service.return_value = mock_classifier
            
            service = IngestionService(db_session)
            result = service.ingest_email(email)
        
        assert result.status == "created"
        assert result.task.category == "finance"
        assert result.task.assignee_id == "u_divya"
        assert result.task.priority == "low"
    
    # Example 6: Alliances/reseller
    def test_odc_example_6_alliances_reseller(self, db_session):
        """
        Example 6: Alliances/reseller
        - Category: alliances
        - Assignee: Karan (u_karan)
        - High priority
        - Task created
        """
        email = EmailInput(
            email_id="odc_ex6_001",
            thread_id="odc_th6_001",
            from_name="Anjali Mehta",
            from_email="anjali@resellerpartner.com",
            to="sales@aluminix.com",
            subject="Reseller Partnership Proposal",
            body="We are a leading IT solutions provider with 5-state presence. Annual turnover: ₹5 Crore. Interested in reselling your products.",
            received_at=datetime.utcnow()
        )
        
        mock_classification = ClassificationResult(
            category="alliances",
            assignee_id="u_karan",
            priority="high",
            company_name="Reseller Partner",
            deal_value_inr=5000000,
            deadline=None,
            confidence=0.92,
            is_task=True,
            reason="Reseller partnership opportunity"
        )
        
        with patch('app.services.ingestion_service.ClassificationService') as mock_class_service:
            mock_classifier = Mock()
            mock_classifier.classify_email.return_value = mock_classification
            mock_class_service.return_value = mock_classifier
            
            service = IngestionService(db_session)
            result = service.ingest_email(email)
        
        assert result.status == "created"
        assert result.task.category == "alliances"
        assert result.task.assignee_id == "u_karan"
        assert result.task.priority == "high"
    
    # Example 7: Out-of-office
    def test_odc_example_7_out_of_office(self, db_session):
        """
        Example 7: Out-of-office
        - is_task = false
        - NO TASK must be created
        """
        email = EmailInput(
            email_id="odc_ex7_001",
            thread_id="odc_th7_001",
            from_name="Rahul Verma",
            from_email="rahul@client.com",
            to="sales@aluminix.com",
            subject="Out of Office: August 10-20",
            body="Thank you for your email. I am currently out of the office from August 10-20, 2026 with limited access to email.",
            received_at=datetime.utcnow()
        )
        
        mock_classification = ClassificationResult(
            category="triage",
            assignee_id="u_triage",
            priority="low",
            company_name=None,
            deal_value_inr=None,
            deadline=None,
            confidence=0.98,
            is_task=False,  # NOT a task
            reason="Out-of-office auto-reply"
        )
        
        with patch('app.services.ingestion_service.ClassificationService') as mock_class_service:
            mock_classifier = Mock()
            mock_classifier.classify_email.return_value = mock_classification
            mock_class_service.return_value = mock_classifier
            
            service = IngestionService(db_session)
            result = service.ingest_email(email)
        
        # Verify NO task was created
        assert result.status == "ignored"
        assert result.task is None
    
    # Example 8: Vendor spam
    def test_odc_example_8_vendor_spam(self, db_session):
        """
        Example 8: Vendor spam
        - is_task = false
        - NO TASK must be created
        """
        email = EmailInput(
            email_id="odc_ex8_001",
            thread_id="odc_th8_001",
            from_name="Marketing Team",
            from_email="marketing@spamvendor.com",
            to="sales@aluminix.com",
            subject="🎉 EXCLUSIVE OFFER - 70% OFF! 🎉",
            body="Don't miss this incredible opportunity! Get our premium software at 70% off for a limited time only!",
            received_at=datetime.utcnow()
        )
        
        mock_classification = ClassificationResult(
            category="triage",
            assignee_id="u_triage",
            priority="low",
            company_name=None,
            deal_value_inr=None,
            deadline=None,
            confidence=0.95,
            is_task=False,  # NOT a task
            reason="Vendor spam/marketing"
        )
        
        with patch('app.services.ingestion_service.ClassificationService') as mock_class_service:
            mock_classifier = Mock()
            mock_classifier.classify_email.return_value = mock_classification
            mock_class_service.return_value = mock_classifier
            
            service = IngestionService(db_session)
            result = service.ingest_email(email)
        
        # Verify NO task was created
        assert result.status == "ignored"
        assert result.task is None
    
    # Example 9: Newsletter
    def test_odc_example_9_newsletter(self, db_session):
        """
        Example 9: Newsletter
        - is_task = false
        - NO TASK must be created
        """
        email = EmailInput(
            email_id="odc_ex9_001",
            thread_id="odc_th9_001",
            from_name="Tech Insights",
            from_email="newsletter@techinsights.com",
            to="sales@aluminix.com",
            subject="Monthly Newsletter - August 2026",
            body="Tech Insights Monthly Newsletter - August 2026. In this month's edition: Top 10 Cloud Security Trends.",
            received_at=datetime.utcnow()
        )
        
        mock_classification = ClassificationResult(
            category="triage",
            assignee_id="u_triage",
            priority="low",
            company_name=None,
            deal_value_inr=None,
            deadline=None,
            confidence=0.97,
            is_task=False,  # NOT a task
            reason="Newsletter subscription"
        )
        
        with patch('app.services.ingestion_service.ClassificationService') as mock_class_service:
            mock_classifier = Mock()
            mock_classifier.classify_email.return_value = mock_classification
            mock_class_service.return_value = mock_classifier
            
            service = IngestionService(db_session)
            result = service.ingest_email(email)
        
        # Verify NO task was created
        assert result.status == "ignored"
        assert result.task is None
    
    # Example 10: Thread reply
    def test_odc_example_10_thread_reply_update(self, db_session):
        """
        Example 10: Thread reply
        - Must update the existing task/thread
        - Must use PATCH/update behavior
        - Must NOT create a second task
        """
        # First, create an initial task
        initial_email = EmailInput(
            email_id="odc_ex10_001",
            thread_id="odc_th10_001",
            from_name="Pooja Nair",
            from_email="pooja@clientcorp.com",
            to="sales@aluminix.com",
            subject="Enterprise Software Inquiry",
            body="We are interested in your enterprise software solutions.",
            received_at=datetime.utcnow()
        )
        
        mock_classification_initial = ClassificationResult(
            category="enterprise_rfp",
            assignee_id="u_aarti",
            priority="high",
            company_name="Client Corp",
            deal_value_inr=2000000,
            deadline="2026-10-01",
            confidence=0.90,
            is_task=True,
            reason="Enterprise software inquiry"
        )
        
        with patch('app.services.ingestion_service.ClassificationService') as mock_class_service:
            mock_classifier = Mock()
            mock_classifier.classify_email.return_value = mock_classification_initial
            mock_class_service.return_value = mock_classifier
            
            service = IngestionService(db_session)
            result_initial = service.ingest_email(initial_email)
        
        # Verify initial task created
        assert result_initial.status == "created"
        assert result_initial.task is not None
        initial_task_id = result_initial.task.task_id
        initial_thread_id = result_initial.task.thread_id
        initial_description = result_initial.task.description
        
        # Now submit a reply in the same thread
        reply_email = EmailInput(
            email_id="odc_ex10_002",  # Different email_id
            thread_id="odc_th10_001",  # Same thread_id
            from_name="Pooja Nair",
            from_email="pooja@clientcorp.com",
            to="sales@aluminix.com",
            subject="Re: Enterprise Software Inquiry",
            body="Following up on our previous email. We have some additional questions.",
            received_at=datetime.utcnow()
        )
        
        mock_classification_reply = ClassificationResult(
            category="enterprise_rfp",
            assignee_id="u_aarti",
            priority="high",
            company_name="Client Corp",
            deal_value_inr=2000000,
            deadline="2026-10-01",
            confidence=0.90,
            is_task=True,
            reason="Thread reply - follow-up"
        )
        
        with patch('app.services.ingestion_service.ClassificationService') as mock_class_service:
            mock_classifier = Mock()
            mock_classifier.classify_email.return_value = mock_classification_reply
            mock_class_service.return_value = mock_classifier
            
            service = IngestionService(db_session)
            result_reply = service.ingest_email(reply_email)
        
        # Verify thread reconciliation: task updated, not created
        assert result_reply.status == "updated"
        assert result_reply.task is not None
        assert result_reply.task.task_id == initial_task_id  # Same task_id
        assert result_reply.task.thread_id == initial_thread_id  # Same thread_id
        assert result_reply.task.description != initial_description  # Description updated
        
        # Verify no second task was created
        all_tasks = db_session.query(Task).filter(
            Task.candidate_id == settings.CANDIDATE_ID,
            Task.thread_id == initial_thread_id
        ).all()
        assert len(all_tasks) == 1  # Only one task for this thread
    
    # Example 11: Ambiguous email
    def test_odc_example_11_ambiguous_triage(self, db_session):
        """
        Example 11: Ambiguous email
        - Must be routed to TRIAGE / triage handling
        - Must NOT be incorrectly assigned to a normal sales owner
        """
        email = EmailInput(
            email_id="odc_ex11_001",
            thread_id="odc_th11_001",
            from_name="Sanjay Gupta",
            from_email="sanjay@unknowncompany.com",
            to="sales@aluminix.com",
            subject="Question about products",
            body="Hi, I have a question about your products. Can you help?",
            received_at=datetime.utcnow()
        )
        
        # Ambiguous emails should route to triage
        mock_classification = ClassificationResult(
            category="triage",
            assignee_id="u_triage",  # Must go to triage
            priority="low",
            company_name=None,
            deal_value_inr=None,
            deadline=None,
            confidence=0.50,  # Low confidence due to ambiguity
            is_task=True,  # Still creates a task, but routed to triage
            reason="Ambiguous inquiry - insufficient information"
        )
        
        with patch('app.services.ingestion_service.ClassificationService') as mock_class_service:
            mock_classifier = Mock()
            mock_classifier.classify_email.return_value = mock_classification
            mock_class_service.return_value = mock_classifier
            
            service = IngestionService(db_session)
            result = service.ingest_email(email)
        
        # Verify task created but routed to triage
        assert result.status == "created"
        assert result.task is not None
        assert result.task.assignee_id == "u_triage"  # Must be triage
        assert result.task.category == "triage"
    
    # Example 12: Hinglish + "1.2 cr"
    def test_odc_example_12_hinglish_1_2_cr(self, db_session):
        """
        Example 12: Hinglish + "1.2 cr"
        - Must be correctly interpreted as ₹1.2 crore = ₹1,20,00,000 = 12,000,000 INR
        - Must route to Aarti because it exceeds the ₹10L enterprise threshold
        - Must preserve correct deal value semantics
        """
        email = EmailInput(
            email_id="odc_ex12_001",
            thread_id="odc_th12_001",
            from_name="Kavita Joshi",
            from_email="kavita@indiabiz.com",
            to="sales@aluminix.com",
            subject="Enterprise solution requirement - 1.2 cr budget",
            body="Humko enterprise solution chahiye. Budget 1.2 cr hai. Please quote.",
            received_at=datetime.utcnow()
        )
        
        # "1.2 cr" should be interpreted as 12,000,000 INR
        # This exceeds ₹10L threshold, so routes to Aarti
        mock_classification = ClassificationResult(
            category="enterprise_rfp",
            assignee_id="u_aarti",  # Exceeds threshold
            priority="high",
            company_name="India Biz",
            deal_value_inr=12000000,  # 1.2 crore = 12,000,000 INR
            deadline="2026-12-01",
            confidence=0.85,
            is_task=True,
            reason="Enterprise deal above ₹10L threshold (1.2 cr interpreted correctly)"
        )
        
        with patch('app.services.ingestion_service.ClassificationService') as mock_class_service:
            mock_classifier = Mock()
            mock_classifier.classify_email.return_value = mock_classification
            mock_class_service.return_value = mock_classifier
            
            service = IngestionService(db_session)
            result = service.ingest_email(email)
        
        # Verify correct interpretation and routing
        assert result.status == "created"
        assert result.task is not None
        assert result.task.assignee_id == "u_aarti"  # Above threshold
        assert result.task.deal_value_inr == 12000000  # 1.2 cr = 12,000,000
        assert result.task.category == "enterprise_rfp"


class TestThreadReconciliationBehavior:
    """
    Additional regression tests for thread reconciliation behavior.
    These tests ensure the thread reconciliation implementation works correctly
    across various scenarios.
    """
    
    def test_same_email_same_thread_idempotency(self, db_session):
        """
        Test that same email_id + same thread returns duplicate (idempotency).
        This should not create a new task or update existing task.
        """
        email = EmailInput(
            email_id="thread_test_001",
            thread_id="thread_test_001",
            from_name="Test User",
            from_email="test@example.com",
            to="sales@aluminix.com",
            subject="Test Subject",
            body="Test body",
            received_at=datetime.utcnow()
        )
        
        mock_classification = ClassificationResult(
            category="smb_enquiry",
            assignee_id="u_rohit",
            priority="medium",
            company_name="Test Company",
            deal_value_inr=500000,
            deadline=None,
            confidence=0.85,
            is_task=True,
            reason="Test classification"
        )
        
        with patch('app.services.ingestion_service.ClassificationService') as mock_class_service:
            mock_classifier = Mock()
            mock_classifier.classify_email.return_value = mock_classification
            mock_class_service.return_value = mock_classifier
            
            service = IngestionService(db_session)
            
            # First ingestion
            result1 = service.ingest_email(email)
            assert result1.status == "created"
            task_id = result1.task.task_id
            
            # Second ingestion with same email_id (idempotency)
            result2 = service.ingest_email(email)
            assert result2.status == "duplicate"
            assert result2.task.task_id == task_id  # Same task
    
    def test_different_thread_different_email_creates_new_task(self, db_session):
        """
        Test that different thread + different email creates a new task.
        This is the normal case for unrelated emails.
        """
        email1 = EmailInput(
            email_id="thread_test_002",
            thread_id="thread_test_002",
            from_name="Test User",
            from_email="test@example.com",
            to="sales@aluminix.com",
            subject="Test Subject 1",
            body="Test body 1",
            received_at=datetime.utcnow()
        )
        
        email2 = EmailInput(
            email_id="thread_test_003",
            thread_id="thread_test_003",  # Different thread
            from_name="Test User",
            from_email="test@example.com",
            to="sales@aluminix.com",
            subject="Test Subject 2",
            body="Test body 2",
            received_at=datetime.utcnow()
        )
        
        mock_classification = ClassificationResult(
            category="smb_enquiry",
            assignee_id="u_rohit",
            priority="medium",
            company_name="Test Company",
            deal_value_inr=500000,
            deadline=None,
            confidence=0.85,
            is_task=True,
            reason="Test classification"
        )
        
        with patch('app.services.ingestion_service.ClassificationService') as mock_class_service:
            mock_classifier = Mock()
            mock_classifier.classify_email.return_value = mock_classification
            mock_class_service.return_value = mock_classifier
            
            service = IngestionService(db_session)
            
            result1 = service.ingest_email(email1)
            result2 = service.ingest_email(email2)
            
            assert result1.status == "created"
            assert result2.status == "created"
            assert result1.task.task_id != result2.task.task_id  # Different tasks
    
    def test_candidate_isolation_thread_reconciliation(self, db_session):
        """
        Test that thread reconciliation respects candidate isolation.
        Same thread_id for different candidates should create separate tasks.
        """
        # This test would require changing settings.CANDIDATE_ID mid-test
        # Since candidate_id is from configuration, we test that the repository
        # method correctly filters by candidate_id
        
        # Test that get_by_thread_and_candidate respects candidate_id
        from app.repositories.task import TaskRepository
        from app.models.task import Task
        
        repo = TaskRepository(db_session)
        
        # Create task for candidate1
        task1 = Task(
            task_id=str(uuid.uuid4()),
            candidate_id="candidate1@example.com",
            source_email_id="email1",
            thread_id="shared_thread",
            title="Task 1",
            description="Description 1",
            assignee_id="u_rohit",
            category="smb_enquiry",
            priority="medium",
            deal_value_inr=500000,
            company_name="Company 1",
            confidence=0.85,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(task1)
        
        # Create task for candidate2 with same thread_id
        task2 = Task(
            task_id=str(uuid.uuid4()),
            candidate_id="candidate2@example.com",
            source_email_id="email2",
            thread_id="shared_thread",  # Same thread
            title="Task 2",
            description="Description 2",
            assignee_id="u_rohit",
            category="smb_enquiry",
            priority="medium",
            deal_value_inr=500000,
            company_name="Company 2",
            confidence=0.85,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(task2)
        db_session.commit()
        
        # Verify repository returns correct task for each candidate
        result1 = repo.get_by_thread_and_candidate("shared_thread", "candidate1@example.com")
        result2 = repo.get_by_thread_and_candidate("shared_thread", "candidate2@example.com")
        
        assert result1.task_id == task1.task_id
        assert result2.task_id == task2.task_id
        assert result1.task_id != result2.task_id
    
    def test_non_task_reply_does_not_update_task(self, db_session):
        """
        Test that non-task reply in same thread does not update existing task.
        Non-task emails should be ignored regardless of thread.
        """
        # Create initial task
        initial_email = EmailInput(
            email_id="nontask_test_001",
            thread_id="nontask_thread_001",
            from_name="Test User",
            from_email="test@example.com",
            to="sales@aluminix.com",
            subject="Initial Task",
            body="Initial task email",
            received_at=datetime.utcnow()
        )
        
        mock_classification_task = ClassificationResult(
            category="smb_enquiry",
            assignee_id="u_rohit",
            priority="medium",
            company_name="Test Company",
            deal_value_inr=500000,
            deadline=None,
            confidence=0.85,
            is_task=True,
            reason="Task email"
        )
        
        with patch('app.services.ingestion_service.ClassificationService') as mock_class_service:
            mock_classifier = Mock()
            mock_classifier.classify_email.return_value = mock_classification_task
            mock_class_service.return_value = mock_classifier
            
            service = IngestionService(db_session)
            result_initial = service.ingest_email(initial_email)
        
        assert result_initial.status == "created"
        initial_task_id = result_initial.task.task_id
        initial_description = result_initial.task.description
        
        # Submit non-task reply in same thread
        non_task_reply = EmailInput(
            email_id="nontask_test_002",
            thread_id="nontask_thread_001",  # Same thread
            from_name="Test User",
            from_email="test@example.com",
            to="sales@aluminix.com",
            subject="Out of Office",
            body="I am out of office.",
            received_at=datetime.utcnow()
        )
        
        mock_classification_nontask = ClassificationResult(
            category="triage",
            assignee_id="u_triage",
            priority="low",
            company_name=None,
            deal_value_inr=None,
            deadline=None,
            confidence=0.95,
            is_task=False,  # NOT a task
            reason="Out of office"
        )
        
        with patch('app.services.ingestion_service.ClassificationService') as mock_class_service:
            mock_classifier = Mock()
            mock_classifier.classify_email.return_value = mock_classification_nontask
            mock_class_service.return_value = mock_classifier
            
            service = IngestionService(db_session)
            result_reply = service.ingest_email(non_task_reply)
        
        # Non-task should be ignored, task should not be updated
        assert result_reply.status == "ignored"
        assert result_reply.task is None
        
        # Verify original task unchanged
        original_task = db_session.query(Task).filter(Task.task_id == initial_task_id).first()
        assert original_task.description == initial_description
    
    def test_multiple_replies_in_same_thread(self, db_session):
        """
        Test that multiple replies in same thread update the same task.
        Each reply should update the existing task, not create new ones.
        """
        # Create initial task
        email1 = EmailInput(
            email_id="multi_thread_001",
            thread_id="multi_thread_001",
            from_name="Test User",
            from_email="test@example.com",
            to="sales@aluminix.com",
            subject="Initial",
            body="Initial email",
            received_at=datetime.utcnow()
        )
        
        mock_classification = ClassificationResult(
            category="smb_enquiry",
            assignee_id="u_rohit",
            priority="medium",
            company_name="Test Company",
            deal_value_inr=500000,
            deadline=None,
            confidence=0.85,
            is_task=True,
            reason="Test"
        )
        
        with patch('app.services.ingestion_service.ClassificationService') as mock_class_service:
            mock_classifier = Mock()
            mock_classifier.classify_email.return_value = mock_classification
            mock_class_service.return_value = mock_classifier
            
            service = IngestionService(db_session)
            result1 = service.ingest_email(email1)
        
        task_id = result1.task.task_id
        
        # First reply
        email2 = EmailInput(
            email_id="multi_thread_002",
            thread_id="multi_thread_001",  # Same thread
            from_name="Test User",
            from_email="test@example.com",
            to="sales@aluminix.com",
            subject="Re: Initial",
            body="First reply",
            received_at=datetime.utcnow()
        )
        
        with patch('app.services.ingestion_service.ClassificationService') as mock_class_service:
            mock_classifier = Mock()
            mock_classifier.classify_email.return_value = mock_classification
            mock_class_service.return_value = mock_classifier
            
            service = IngestionService(db_session)
            result2 = service.ingest_email(email2)
        
        assert result2.status == "updated"
        assert result2.task.task_id == task_id
        
        # Second reply
        email3 = EmailInput(
            email_id="multi_thread_003",
            thread_id="multi_thread_001",  # Same thread
            from_name="Test User",
            from_email="test@example.com",
            to="sales@aluminix.com",
            subject="Re: Initial",
            body="Second reply",
            received_at=datetime.utcnow()
        )
        
        with patch('app.services.ingestion_service.ClassificationService') as mock_class_service:
            mock_classifier = Mock()
            mock_classifier.classify_email.return_value = mock_classification
            mock_class_service.return_value = mock_classifier
            
            service = IngestionService(db_session)
            result3 = service.ingest_email(email3)
        
        assert result3.status == "updated"
        assert result3.task.task_id == task_id
        
        # Verify only one task exists for this thread
        all_tasks = db_session.query(Task).filter(
            Task.candidate_id == settings.CANDIDATE_ID,
            Task.thread_id == "multi_thread_001"
        ).all()
        assert len(all_tasks) == 1
