from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
    preferences: Optional[dict] = None
    
    class Config:
        from_attributes = True


class UserPreferences(BaseModel):
    priority_threshold_urgent: float = 80.0
    priority_threshold_high: float = 60.0
    priority_threshold_normal: float = 40.0
    auto_respond: bool = False
    response_tone: str = "professional"
    preferred_language: str = "en"
