"""Fetch emails via IMAP (Gmail or generic)."""

from typing import List, Optional, Tuple

from backend.app.services.email_service import EmailService


def _detect_imap_host(email: str) -> Tuple[str, int]:
    """Return (host, port) for common providers."""
    email_lower = email.strip().lower()
    if "gmail" in email_lower or "googlemail" in email_lower:
        return "imap.gmail.com", 993
    if "outlook" in email_lower or "hotmail" in email_lower or "live" in email_lower:
        return "outlook.office365.com", 993
    if "yahoo" in email_lower:
        return "imap.mail.yahoo.com", 993
    return "imap.gmail.com", 993  # default to Gmail


def fetch_emails(
    email: str,
    password: str,
    limit: int = 10,
    host: Optional[str] = None,
    port: Optional[int] = None,
) -> List[dict]:
    """
    Connect via IMAP, fetch recent emails, parse and return list of dicts
    compatible with EmailService.parse_email / EmailCreate.
    Uses app password for Gmail (2FA required).
    """
    try:
        from imapclient import IMAPClient
    except ImportError:
        raise RuntimeError("imapclient not installed. Run: pip install imapclient")

    if not host or not port:
        host, port = _detect_imap_host(email)

    out: List[dict] = []
    with IMAPClient(host, port=port, use_uid=True, ssl=True) as client:
        client.login(email.strip(), password)
        client.select_folder("INBOX")
        messages = client.search(["ALL"])
        if not messages:
            return []
        # fetch newest first
        to_fetch = list(reversed(messages))[:limit]
        raw = client.fetch(to_fetch, ["RFC822"])
        for uid, data in raw.items():
            rfc = data.get(b"RFC822")
            if not rfc:
                continue
            raw_str = rfc.decode("utf-8", errors="replace") if isinstance(rfc, bytes) else str(rfc)
            try:
                parsed = EmailService.parse_email(raw_str)
                out.append(parsed)
            except Exception:
                continue
    return out
