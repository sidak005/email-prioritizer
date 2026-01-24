from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class PriorityLevel(str, Enum):
    """Email priority levels"""
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    SPAM = "spam"


class EmailIntent(str, Enum):
    """Email intent types"""
    ACTION_REQUIRED = "action_required"
    QUESTION = "question"
    MEETING = "meeting"
    NEWSLETTER = "newsletter"
    PROMOTIONAL = "promotional"
    SPAM = "spam"
    INFORMATION = "information"


class EmailCreate(BaseModel):
    """Model for creating/analyzing an email"""
    subject: str
    body: str
    sender: str
    recipient: Optional[str] = None
    received_at: datetime = datetime.now()
    html_body: Optional[str] = None


class Email(BaseModel):
    """Full email model"""
    id: str
    user_id: Optional[str] = None
    subject: str
    sender: str
    recipient: str
    body: str
    html_body: Optional[str] = None
    priority_score: float = 0.0
    priority_level: PriorityLevel = PriorityLevel.NORMAL
    intent: Optional[str] = None
    sentiment: Optional[str] = None
    is_read: bool = False
    is_archived: bool = False
    received_at: datetime
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class EmailAnalysis(BaseModel):
    """Email analysis result"""
    email_id: str
    priority_score: float
    priority_level: PriorityLevel
    intent: str
    sentiment: str
    urgency_keywords: List[str] = []
    sender_importance: float = 0.5
    processing_time_ms: float = 0.0


class FetchInboxRequest(BaseModel):
    """Request model for fetching emails via IMAP"""
    email: str
    password: str
    limit: int = 10


class EmailPriorityUpdate(BaseModel):
    """Model for updating email priority"""
    priority_score: Optional[float] = None
    priority_level: Optional[PriorityLevel] = None
    user_feedback: Optional[str] = None  # "correct" or "incorrect"
