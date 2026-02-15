import re

def extract_contact_info(text: str) -> dict:
    """
    Extracts recruiter email, name (approximate), and application form URLs from text.
    
    Args:
        text (str): The job description or text to search.
        
    Returns:
        dict: A dictionary with keys 'recruiter_email', 'recruiter_name', 'application_form_url'.
    """
    info = {
        "recruiter_email": "",
        "recruiter_name": "",
        "application_form_url": ""
    }
    
    if not text:
        return info

    # 1. Extract Email
    # Common regex for email
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    
    # Filter out common false positives if necessary (e.g. example.com)
    valid_emails = [e for e in emails if not e.endswith('example.com')]
    
    if valid_emails:
        info['recruiter_email'] = valid_emails[0]
        
    # 2. Extract Application Form URL
    # Look for google forms, typeform, airtable, etc.
    form_patterns = [
        r'(https?://docs\.google\.com/forms/d/[a-zA-Z0-9_-]+/viewform)',
        r'(https?://forms\.gle/[a-zA-Z0-9]+)',
        r'(https?://[\w-]+\.typeform\.com/to/[\w]+)',
        r'(https?://airtable\.com/[\w]+)',
        r'(https?://[\w-]+\.tally\.so/r/[\w]+)'
    ]
    
    for pattern in form_patterns:
        match = re.search(pattern, text)
        if match:
            info['application_form_url'] = match.group(1)
            break
            
    # 3. Extract Recruiter Name (Very rudimentary)
    # This is hard with just regex. We'll look for "Contact: [Name]" or "Hiring Manager: [Name]"
    # or "Reach out to [Name]"
    # For now, let's try a simple pattern or leave it for LLM extraction later if accurate.
    # LLM is better for name.
    
    # Simple heuristic: "Contact: John Doe"
    name_patterns = [
        r'(?:Contact|Reach out to|Hiring Manager):\s*([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)'
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, text)
        if match:
            # simple check to ensure it's not "Me" or "Us"
            name = match.group(1)
            if len(name) > 3 and " " in name: # assume at least first and last name
                 info['recruiter_name'] = name
                 break

    return info
