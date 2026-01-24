from supabase import create_client, Client
from backend.app.config import settings
from typing import Optional, Dict, List
from datetime import datetime


class SupabaseClient:
    def __init__(self):
        self.client: Optional[Client] = None
    
    def initialize(self):
        """Initialize Supabase client"""
        try:
            self.client = create_client(settings.supabase_url, settings.supabase_key)
            print("✅ Supabase client initialized")
        except Exception as e:
            print(f"❌ Error initializing Supabase: {e}")
            raise
    
    async def create_email(self, email_data: Dict) -> Dict:
        """Create a new email record"""
        try:
            result = self.client.table("emails").insert(email_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating email: {e}")
            raise
    
    async def get_email(self, email_id: str) -> Optional[Dict]:
        """Get email by ID"""
        try:
            result = self.client.table("emails").select("*").eq("id", email_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting email: {e}")
            return None
    
    async def update_email(self, email_id: str, updates: Dict) -> Dict:
        """Update email record"""
        try:
            result = self.client.table("emails").update(updates).eq("id", email_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error updating email: {e}")
            raise
    
    async def get_user_emails(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        priority_level: Optional[str] = None
    ) -> List[Dict]:
        """Get emails for a user"""
        try:
            query = self.client.table("emails").select("*").eq("user_id", user_id)
            
            if priority_level:
                query = query.eq("priority_level", priority_level)
            
            query = query.order("priority_score", desc=True).limit(limit).offset(offset)
            result = query.execute()
            
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting user emails: {e}")
            return []
    
    async def create_user(self, user_data: Dict) -> Dict:
        """Create a new user"""
        try:
            result = self.client.table("users").insert(user_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating user: {e}")
            raise
    
    async def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        try:
            result = self.client.table("users").select("*").eq("id", user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
