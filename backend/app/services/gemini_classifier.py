import json
from typing import Optional
from google import genai
from app.config import settings
from app.schemas.email import EmailInput
from app.schemas.classification import ClassificationResult, VALID_ASSIGNEE_IDS, VALID_CATEGORIES, VALID_PRIORITIES
from app.utils.logging import setup_logging

logger = setup_logging()


class GeminiClassifier:
    """Service for classifying emails using Gemini AI."""
    
    def __init__(self):
        """Initialize Gemini classifier with API key from environment."""
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
            logger.info(f"Gemini classifier initialized with model: {self.model_name}")
        else:
            logger.warning("GEMINI_API_KEY not configured, classifier will not work")
            self.client = None
    
    def _build_classification_prompt(self, email: EmailInput) -> str:
        """Build the classification prompt for Gemini."""
        prompt = f"""
You are an email classification system for a sales inbox. Analyze the following email and classify it according to strict rules.

EMAIL DETAILS:
- From: {email.from_name} ({email.from_email})
- To: {email.to}
- Subject: {email.subject}
- Body: {email.body}
- Thread ID: {email.thread_id}

CLASSIFICATION RULES:

1. Determine if this email should create a task (is_task):
   - Set is_task=false for: out-of-office/autoreply messages, newsletters, vendor spam, generic unsolicited marketing spam, or other clearly non-actionable automated messages
   - Set is_task=true for: actionable business communications that require follow-up

2. If is_task=true, assign to one of these employees:
   - u_aarti: enterprise RFPs, RFIs, tenders, inbound deals above ₹10,00,000
   - u_rohit: SMB enquiries, demo requests, deals at or below ₹10,00,000
   - u_meera: marketing, webinars, event/conference sponsorships, PR, media/content collaborations
   - u_karan: reseller proposals, channel partnerships, technology integrations
   - u_divya: invoices, GST, payments, purchase orders, vendor billing
   - u_triage: ambiguous cases, insufficient information, or when uncertain

3. Assign category (one of):
   - enterprise_rfp, smb_enquiry, marketing, alliances, finance, triage

4. Assign priority (one of):
   - high, medium, low

5. Extract if available:
   - company_name: the company name mentioned
   - deal_value_inr: deal value in INR (integer only)
   - deadline: deadline date in YYYY-MM-DD format

6. Provide:
   - confidence: float between 0.0 and 1.0 (be conservative)
   - reason: short explanation of classification

IMPORTANT:
- Understand the meaning of the email, don't just search for keywords
- When uncertain, prefer triage rather than inventing information
- Use conservative classification
- If confidence is below 0.6, route to u_triage
- If is_task=false, do not assign to an employee

Return ONLY valid JSON in this exact format:
{{
    "category": "enterprise_rfp",
    "assignee_id": "u_aarti",
    "priority": "high",
    "company_name": "Company Name",
    "deal_value_inr": 1500000,
    "deadline": "2026-09-15",
    "confidence": 0.85,
    "is_task": true,
    "reason": "Enterprise RFP for document management system, deal value above threshold"
}}
"""
        return prompt
    
    def classify(self, email: EmailInput) -> ClassificationResult:
        """Classify an email using Gemini."""
        if not self.client:
            raise ValueError("Gemini classifier not initialized - GEMINI_API_KEY not configured")
        
        result_text = ""
        try:
            prompt = self._build_classification_prompt(email)
            
            # Generate response with structured output using new SDK
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={"temperature": 0.1, "response_mime_type": "application/json"}  # Request JSON output
            )
            
            # Parse JSON response
            result_text = response.text.strip()
            result_dict = json.loads(result_text)
            
            # Validate and create ClassificationResult
            classification = ClassificationResult(**result_dict)
            
            logger.info(f"Classified email {email.email_id}: category={classification.category}, assignee={classification.assignee_id}, is_task={classification.is_task}")
            
            return classification
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            logger.error(f"Response text: {result_text}")
            raise ValueError("Invalid JSON response from Gemini")
        except Exception as e:
            logger.error(f"Error classifying email: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if Gemini classifier is available."""
        return self.client is not None
