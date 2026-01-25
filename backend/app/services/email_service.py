from typing import List, Optional
from datetime import datetime
import email
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup
from backend.app.models.email import Email, EmailCreate, PriorityLevel, EmailIntent


class EmailService:
    """Service for email parsing and processing"""
    
    def parse_email(raw_email: str) -> dict:
        """Parse raw email string into structured data"""
        msg = email.message_from_string(raw_email)
        
        # Extract headers
        subject = msg.get("Subject", "")
        sender = msg.get("From", "")
        recipient = msg.get("To", "")
        date_str = msg.get("Date", "")
        
        # Parse date
        try:
            received_at = parsedate_to_datetime(date_str)
        except (ValueError, TypeError):
            received_at = datetime.now()
        
        # Extract body
        body = ""
        html_body = None
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))
                
                if "attachment" not in content_disposition:
                    if content_type == "text/plain":
                        body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                    elif content_type == "text/html":
                        html_body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
        else:
            content_type = msg.get_content_type()
            if content_type == "text/plain":
                body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
            elif content_type == "text/html":
                html_body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
        
        # Clean HTML if present
        if html_body:
            soup = BeautifulSoup(html_body, "html.parser")
            # Remove scripts and styles
            for script in soup(["script", "style"]):
                script.decompose()
            # Get text
            if not body:
                body = soup.get_text(separator=" ", strip=True)
        
        # Clean body (remove signatures, etc.)
        body = EmailService._clean_email_body(body)
        
        return {
            "subject": subject,
            "sender": EmailService._extract_email_address(sender),
            "recipient": EmailService._extract_email_address(recipient),
            "body": body,
            "html_body": html_body,
            "received_at": received_at
        }
    
    def _clean_email_body(body: str) -> str:
        """Clean email body (remove signatures, etc.)"""
        if not body:
            return ""
        
        # Remove common signature patterns
        lines = body.split("\n")
        cleaned_lines = []
        signature_started = False
        
        for line in lines:
            # Common signature indicators
            if any(indicator in line.lower() for indicator in [
                "sent from", "best regards", "sincerely", 
                "--", "---", "this email was sent"
            ]):
                signature_started = True
            
            if not signature_started:
                cleaned_lines.append(line)
        
        return "\n".join(cleaned_lines).strip()
    
    def _extract_email_address(address_string: str) -> str:
        """Extract email address from 'Name <email@domain.com>' format"""
        import re
        # Try to extract email from angle brackets
        match = re.search(r'<(.+?)>', address_string)
        if match:
            return match.group(1)
        # Otherwise return as is
        return address_string.strip()
