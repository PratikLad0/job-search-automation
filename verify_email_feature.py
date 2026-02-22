import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Allow imports from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from backend.app.services.parsers.utils import extract_contact_info
from backend.app.db.models import Job, UserProfile

class TestEmailFeature(unittest.TestCase):
    def test_extract_contact_info(self):
        text = """
        We are looking for a developer.
        Contact: Jane Doe at jane.doe@techcorp.com
        To apply, visit https://forms.gle/ABC12345
        """
        info = extract_contact_info(text)
        print(f"Extracted: {info}")
        self.assertEqual(info['recruiter_email'], "jane.doe@techcorp.com")
        self.assertEqual(info['recruiter_name'], "Jane Doe")
        self.assertEqual(info['application_form_url'], "https://forms.gle/ABC12345")

    @patch('backend.app.services.generators.email_generator.get_ai')
    def test_email_generation(self, mock_get_ai):
        mock_ai = MagicMock()
        mock_ai.generate.return_value = "Subject: Application\n\nDear Jane..."
        mock_get_ai.return_value = mock_ai
        
        from backend.app.services.generators.email_generator import generate_application_email
        
        job = Job(
            title="Senior Dev", 
            company="TechCorp", 
            description="Great job.",
            recruiter_name="Jane Doe", 
            recruiter_email="jane@techcorp.com"
        )
        profile = UserProfile(full_name="Candidate One", email="me@example.com")
        
        draft = generate_application_email(job, profile)
        print(f"Draft: {draft}")
        self.assertIn("Subject: Application", draft)

if __name__ == '__main__':
    unittest.main()
