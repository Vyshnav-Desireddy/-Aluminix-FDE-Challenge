import random
import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from app.schemas.email import EmailInput


class SampleEmailGenerator:
    """Service for generating realistic sample sales emails for testing."""
    
    # Email templates for different categories
    TEMPLATES = {
        "enterprise_rfp": [
            {
                "subject": "Request for Proposal - Document Management System",
                "body": """Dear Team,

We are issuing a Request for Proposal (RFP) for a comprehensive document management system for our organization.

Requirements:
- Support for 500+ concurrent users
- Advanced search and indexing capabilities
- Integration with existing ERP systems
- Compliance with ISO 27001 standards
- Budget: ₹25,00,000 - ₹30,00,000

Timeline:
- Proposal submission deadline: September 15, 2026
- Implementation start: November 2026
- Completion: March 2027

Please submit your proposal including technical specifications, implementation timeline, and commercial terms.

Best regards,
{sender_name}
{company}""",
                "deal_value": 2500000,
                "assignee": "u_aarti"
            },
            {
                "subject": "RFP: Enterprise CRM Implementation",
                "body": """Hello,

We are seeking proposals for a full-scale CRM implementation for our enterprise operations.

Scope:
- 2000+ user licenses
- Multi-location deployment (5 offices)
- Custom workflow automation
- Advanced analytics and reporting
- Integration with SAP ERP
- Budget range: ₹40,00,000 - ₹50,00,000

Key dates:
- RFP response due: October 20, 2026
- Vendor selection: November 2026
- Project kickoff: December 2026

Interested vendors should submit detailed proposals with case studies of similar implementations.

Regards,
{sender_name}
{company}""",
                "deal_value": 4500000,
                "assignee": "u_aarti"
            }
        ],
        "smb_enquiry": [
            {
                "subject": "Product Demo Request - Cloud Solutions",
                "body": """Hi there,

I came across your cloud solutions and would like to schedule a demo for our team.

We are a growing SME with 25 employees looking to:
- Migrate our on-premise systems to cloud
- Implement collaboration tools
- Set up secure remote access
- Budget: ₹5,00,000 - ₹8,00,000

Could you please schedule a demo next week? We're available Tuesday or Thursday afternoons.

Thanks,
{sender_name}
{company}""",
                "deal_value": 650000,
                "assignee": "u_rohit"
            },
            {
                "subject": "Quote Request - IT Infrastructure Upgrade",
                "body": """Hello,

We need a quote for upgrading our IT infrastructure.

Current setup:
- 15 desktop computers (5+ years old)
- 1 server (end of life)
- Basic network equipment

Requirements:
- 15 new workstations with monitors
- 1 new server with RAID configuration
- Network switch upgrade
- Installation and data migration
- Budget: ₹8,00,000

Please provide a detailed quote with product specifications and warranty information.

Best,
{sender_name}
{company}""",
                "deal_value": 800000,
                "assignee": "u_rohit"
            }
        ],
        "marketing": [
            {
                "subject": "Webinar Sponsorship Opportunity - Tech Summit 2026",
                "body": """Dear Marketing Team,

We are organizing the Tech Summit 2026, a premier technology conference expected to attract 500+ industry professionals.

Sponsorship opportunities:
- Gold Sponsor: ₹3,00,000 (logo placement, speaking slot, booth)
- Silver Sponsor: ₹1,50,000 (logo placement, booth)
- Bronze Sponsor: ₹75,000 (logo placement)

Event details:
- Date: November 15-16, 2026
- Venue: Convention Center, Mumbai
- Expected attendees: 500+ CTOs, IT managers, and decision makers

We would love to discuss partnership opportunities with your organization.

Best regards,
{sender_name}
{company}""",
                "deal_value": 300000,
                "assignee": "u_meera"
            },
            {
                "subject": "Content Collaboration Proposal",
                "body": """Hi,

We run a popular technology blog with 50,000 monthly readers and are looking for content collaboration opportunities.

Collaboration options:
- Sponsored articles: ₹25,000 per article
- Product reviews: ₹40,000 per review
- Newsletter mentions: ₹15,000 per mention
- Annual partnership: ₹2,00,000 (includes all above)

Our audience consists of IT decision-makers and business owners looking for technology solutions.

Would you be interested in exploring a partnership?

Regards,
{sender_name}
{company}""",
                "deal_value": 200000,
                "assignee": "u_meera"
            }
        ],
        "alliances": [
            {
                "subject": "Reseller Partnership Proposal",
                "body": """Dear Partnerships Team,

We are a leading IT solutions provider with presence across 5 states in India and are interested in becoming a reseller for your products.

Our credentials:
- 10+ years in IT solutions
- 50+ enterprise clients
- Annual turnover: ₹5 Crore
- Technical team of 20 certified engineers
- Strong relationships with 200+ SMBs

We are interested in reselling:
- Your cloud solutions
- Security products
- Collaboration tools

Please share your reseller program details and terms.

Best regards,
{sender_name}
{company}""",
                "deal_value": 5000000,
                "assignee": "u_karan"
            },
            {
                "subject": "Technology Integration Partnership",
                "body": """Hello,

We have developed a complementary technology that integrates well with your platform and would like to discuss a technology partnership.

Our solution:
- AI-powered analytics add-on
- Seamless API integration
- Proven ROI improvement of 25%
- Currently used by 100+ customers

Participation model:
- Revenue sharing: 70/30 split
- Co-marketing activities
- Joint sales calls
- Technical support collaboration

Would you be open to a discussion about integrating our solutions?

Regards,
{sender_name}
{company}""",
                "deal_value": 1500000,
                "assignee": "u_karan"
            }
        ],
        "finance": [
            {
                "subject": "Invoice #INV-2026-089 - Payment Due",
                "body": """Dear Finance Team,

Please find attached invoice #INV-2026-089 for services rendered in July 2026.

Invoice details:
- Invoice amount: ₹1,25,000
- Due date: August 25, 2026
- Services: Cloud infrastructure and support
- Payment terms: Net 30 days

Bank details for payment:
- Bank: HDFC Bank
- Account: 1234567890
- IFSC: HDFC0001234
- GSTIN: 29ABCDE1234F1Z5

Please process payment by the due date to avoid late payment charges.

Best regards,
{sender_name}
{company}""",
                "deal_value": 125000,
                "assignee": "u_divya"
            },
            {
                "subject": "Purchase Order #PO-2026-156 - Software Licenses",
                "body": """Hello,

Please find attached Purchase Order #PO-2026-156 for software licenses.

PO details:
- PO amount: ₹3,50,000
- Items: 50 user licenses (Annual subscription)
- Delivery: Immediate (electronic delivery)
- Billing address: As per company records
- GST: 18% applicable

Please acknowledge receipt and provide invoice with PO reference.

Our GSTIN: 29ABCDE1234F1Z5

Regards,
{sender_name}
{company}""",
                "deal_value": 350000,
                "assignee": "u_divya"
            }
        ],
        "non_task": [
            {
                "subject": "Out of Office: August 10-20",
                "body": """Hello,

Thank you for your email. I am currently out of the office from August 10-20, 2026 with limited access to email.

For urgent matters, please contact my colleague at alternate@example.com or call +91-9876543210.

I will respond to your email upon my return on August 21, 2026.

Best regards,
{sender_name}""",
                "deal_value": None,
                "assignee": "u_triage"
            },
            {
                "subject": "Monthly Newsletter - August 2026",
                "body": """Tech Insights Monthly Newsletter - August 2026

In this month's edition:
- Top 10 Cloud Security Trends
- AI in Business: What You Need to Know
- Case Study: Digital Transformation Success
- Upcoming Webinars and Events

Subscribe to our premium newsletter for in-depth analysis and exclusive content.

Unsubscribe: Click here to unsubscribe from this newsletter.

© 2026 Tech Insights""",
                "deal_value": None,
                "assignee": "u_triage"
            },
            {
                "subject": "Special Offer - Limited Time Only!",
                "body": """🎉 EXCLUSIVE OFFER - 70% OFF! 🎉

Dear Customer,

Don't miss this incredible opportunity! Get our premium software at 70% off for a limited time only!

✅ Original price: ₹50,000
✅ Offer price: ₹15,000
✅ Valid until: Today!

Click here to claim your offer now!

This is not a spam email. You have been selected for this exclusive offer.

Best,
Marketing Team""",
                "deal_value": None,
                "assignee": "u_triage"
            }
        ]
    }
    
    # Company names for realistic emails
    COMPANIES = [
        "Meridian Steel Pvt Ltd",
        "Tech Solutions India",
        "Global Systems Corp",
        "Innovate Technologies",
        "Apex Software Solutions",
        "Prime IT Services",
        "Nexus Digital",
        "Summit Consulting",
        "Pinnacle Technologies",
        "Vertex Solutions"
    ]
    
    # Sender names
    SENDER_NAMES = [
        "Rajesh Kumar",
        "Priya Sharma",
        "Amit Patel",
        "Sneha Reddy",
        "Vikram Singh",
        "Anjali Mehta",
        "Rahul Verma",
        "Pooja Nair",
        "Sanjay Gupta",
        "Kavita Joshi"
    ]
    
    # Email domains
    EMAIL_DOMAINS = [
        "gmail.com",
        "yahoo.com",
        "outlook.com",
        "company.com",
        "techcorp.in",
        "solutions.co.in"
    ]
    
    def __init__(self):
        """Initialize the sample email generator."""
        pass
    
    def generate_email(
        self,
        category: Optional[str] = None,
        company_name: Optional[str] = None,
        sender_name: Optional[str] = None
    ) -> EmailInput:
        """
        Generate a single sample email.
        
        Args:
            category: Optional category to generate email for. If None, randomly selects from all categories.
            company_name: Optional company name to use. If None, randomly selects from predefined list.
            sender_name: Optional sender name to use. If None, randomly selects from predefined list.
        
        Returns:
            EmailInput object with generated email data.
        """
        # Select category
        if category is None:
            all_categories = list(self.TEMPLATES.keys())
            category = random.choice(all_categories)
        
        # Get templates for category
        templates = self.TEMPLATES.get(category, self.TEMPLATES["non_task"])
        template = random.choice(templates)
        
        # Generate company and sender
        if company_name is None:
            company_name = random.choice(self.COMPANIES)
        if sender_name is None:
            sender_name = random.choice(self.SENDER_NAMES)
        
        # Generate email and thread IDs
        email_id = f"em_{uuid.uuid4().hex[:12]}"
        thread_id = f"th_{uuid.uuid4().hex[:12]}"
        
        # Generate sender email
        from_email = f"{sender_name.lower().replace(' ', '.')}@{random.choice(self.EMAIL_DOMAINS)}"
        
        # Fill in template
        subject = template["subject"]
        body = template["body"].format(
            sender_name=sender_name,
            company=company_name
        )
        
        # Generate received timestamp (within last 30 days)
        received_at = datetime.utcnow() - timedelta(days=random.randint(0, 30))
        
        return EmailInput(
            email_id=email_id,
            thread_id=thread_id,
            from_name=sender_name,
            from_email=from_email,
            to="sales@aluminix.com",
            subject=subject,
            body=body,
            received_at=received_at
        )
    
    def generate_emails(
        self,
        count: int,
        category: Optional[str] = None,
        shuffle: bool = True
    ) -> List[EmailInput]:
        """
        Generate multiple sample emails.
        
        Args:
            count: Number of emails to generate.
            category: Optional category to generate emails for. If None, randomly selects from all categories.
            shuffle: Whether to shuffle the generated emails.
        
        Returns:
            List of EmailInput objects.
        """
        emails = []
        
        if category:
            # Generate all emails of the same category
            for _ in range(count):
                emails.append(self.generate_email(category=category))
        else:
            # Generate emails from different categories
            all_categories = list(self.TEMPLATES.keys())
            for _ in range(count):
                emails.append(self.generate_email(category=random.choice(all_categories)))
        
        if shuffle:
            random.shuffle(emails)
        
        return emails
    
    def get_available_categories(self) -> List[str]:
        """Get list of available email categories."""
        return list(self.TEMPLATES.keys())
