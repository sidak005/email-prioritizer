from fastapi import APIRouter, HTTPException
from backend.app.models.email import EmailPriorityUpdate
from backend.app.database.supabase_client import SupabaseClient
from backend.app.utils.metrics import MetricsCollector

router = APIRouter()
metrics = MetricsCollector()


@router.post("/{email_id}/feedback")
async def update_priority_feedback(email_id: str, feedback: EmailPriorityUpdate):
    """Update priority based on user feedback"""
    from backend.app.database.supabase_client import SupabaseClient
    
    try:
        supabase_client = SupabaseClient()
        supabase_client.initialize()
        
        updates = {}
        if feedback.priority_score is not None:
            updates["priority_score"] = feedback.priority_score
        if feedback.priority_level is not None:
            updates["priority_level"] = feedback.priority_level
        
        # Update in database
        await supabase_client.update_email(email_id, updates)
        
        # Record feedback for accuracy metrics
        if feedback.user_feedback:
            is_correct = feedback.user_feedback == "correct"
            metrics.record_priority_feedback(is_correct)
        
        return {"message": "Feedback recorded", "email_id": email_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
