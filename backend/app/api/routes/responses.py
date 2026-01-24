from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.app.services.llm_service import LLMService
from backend.app.utils.metrics import MetricsCollector

router = APIRouter()
llm_service = LLMService()
metrics = MetricsCollector()


class ResponseRequest(BaseModel):
    email_subject: str
    email_body: str
    tone: Optional[str] = "professional"


class ResponseReply(BaseModel):
    generated_response: str
    tone: str


@router.post("/generate", response_model=ResponseReply)
async def generate_response(request: ResponseRequest):
    """Generate email response"""
    from backend.app.services.llm_service import LLMService
    
    try:
        llm_service = LLMService()
        if llm_service.sentiment_analyzer is None:
            await llm_service.initialize()
        
        response = await llm_service.generate_response(
            email_subject=request.email_subject,
            email_body=request.email_body,
            tone=request.tone
        )
        
        metrics.record_response_generation()
        
        return ResponseReply(
            generated_response=response,
            tone=request.tone
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
