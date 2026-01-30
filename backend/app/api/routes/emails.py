from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import uuid
from datetime import datetime
import time

from backend.app.models.email import Email, EmailCreate, EmailAnalysis, FetchInboxRequest
from backend.app.services.email_service import EmailService
from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.pinecone_service import PineconeService
from backend.app.services.priority_service import PriorityService
from backend.app.services.llm_service import LLMService
from backend.app.database.supabase_client import SupabaseClient
from backend.app.utils.metrics import MetricsCollector
from backend.app.services.imap_service import fetch_emails

router = APIRouter()
metrics = MetricsCollector()


@router.post("/analyze", response_model=EmailAnalysis)
async def analyze_email(email_data: EmailCreate):
    """Analyze a single email and return priority score"""
    start_time = time.time()
    
    try:
        # Initialize services
        embedding_service = EmbeddingService()
        if embedding_service.model is None:
            await embedding_service.initialize()
        
        pinecone_service = PineconeService()
        if pinecone_service.index is None:
            await pinecone_service.initialize()
        
        llm_service = LLMService()
        if llm_service.sentiment_analyzer is None:
            await llm_service.initialize()
        
        # Calculate priority
        priority_service = PriorityService(
            embedding_service,
            pinecone_service,
            llm_service
        )
        
        analysis = await priority_service.calculate_priority(
            subject=email_data.subject,
            body=email_data.body,
            sender=email_data.sender,
            received_at=email_data.received_at,
            user_id="default_user"  # TODO: Get from auth
        )
        
        # Generate embedding and store in Pinecone
        embedding = embedding_service.generate_embedding(
            f"{email_data.subject} {email_data.body}"
        )
        
        email_id = str(uuid.uuid4())
        await pinecone_service.upsert_email_embedding(
            email_id=email_id,
            embedding=embedding,
            metadata={
                "subject": email_data.subject,
                "sender": email_data.sender,
                "priority_score": analysis["priority_score"],
                "priority_level": analysis["priority_level"],
                "intent": analysis["intent"],
                "received_at": email_data.received_at.isoformat()
            }
        )
        
        # Record metrics
        latency = (time.time() - start_time) * 1000
        metrics.record_email_processing(latency, success=True)
        
        return EmailAnalysis(
            email_id=email_id,
            **analysis
        )
        
    except Exception as e:
        latency = (time.time() - start_time) * 1000
        metrics.record_email_processing(latency, success=False)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-analyze")
async def batch_analyze_emails(emails: List[EmailCreate]):
    results = []
    
    for email_data in emails:
        try:
            # Reuse analyze_email logic
            import time
            start_time = time.time()
            
            embedding_service = EmbeddingService()
            if embedding_service.model is None:
                await embedding_service.initialize()
            
            pinecone_service = PineconeService()
            if pinecone_service.index is None:
                await pinecone_service.initialize()
            
            llm_service = LLMService()
            if llm_service.sentiment_analyzer is None:
                await llm_service.initialize()
            
            priority_service = PriorityService(
                embedding_service,
                pinecone_service,
                llm_service
            )
            
            analysis = await priority_service.calculate_priority(
                subject=email_data.subject,
                body=email_data.body,
                sender=email_data.sender,
                received_at=email_data.received_at,
                user_id="default_user"
            )
            
            email_id = str(uuid.uuid4())
            embedding = embedding_service.generate_embedding(
                f"{email_data.subject} {email_data.body}"
            )
            
            await pinecone_service.upsert_email_embedding(
                email_id=email_id,
                embedding=embedding,
                metadata={
                    "subject": email_data.subject,
                    "sender": email_data.sender,
                    "priority_score": analysis["priority_score"],
                    "priority_level": analysis["priority_level"],
                    "intent": analysis["intent"],
                    "received_at": email_data.received_at.isoformat()
                }
            )
            
            latency = (time.time() - start_time) * 1000
            metrics.record_email_processing(latency, success=True)
            
            results.append({
                "email_id": email_id,
                **analysis
            })
        except Exception as e:
            results.append({"error": str(e)})
    
    return {"results": results, "total": len(results)}


@router.post("/fetch")
async def fetch_inbox(req: FetchInboxRequest):
    """Fetch recent emails via IMAP, analyze each, and return results."""
    import asyncio
    import time

    def _fetch():
        return fetch_emails(req.email, req.password, limit=req.limit)

    try:
        parsed_list = await asyncio.to_thread(_fetch)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"IMAP fetch failed: {e}")

    if not parsed_list:
        return {"results": [], "total": 0}

    embedding_service = EmbeddingService()
    if embedding_service.model is None:
        await embedding_service.initialize()
    pinecone_service = PineconeService()
    if pinecone_service.index is None:
        await pinecone_service.initialize()
    llm_service = LLMService()
    if llm_service.sentiment_analyzer is None:
        await llm_service.initialize()
    priority_service = PriorityService(
        embedding_service,
        pinecone_service,
        llm_service,
    )

    results = []
    for p in parsed_list:
        try:
            recipient = (p.get("recipient") or "").strip()
            if not recipient or "@" not in recipient:
                recipient = "user@example.com"
            sender = (p.get("sender") or "").strip() or "unknown@example.com"
            subject = (p.get("subject") or "").strip() or "(No subject)"
            body = (p.get("body") or "").strip() or "(No body)"
            received_at = p.get("received_at") or datetime.now()
            if not hasattr(received_at, "isoformat"):
                received_at = datetime.now()

            start = time.time()
            analysis = await priority_service.calculate_priority(
                subject=subject,
                body=body,
                sender=sender,
                received_at=received_at,
                user_id="default_user",
            )
            embedding = embedding_service.generate_embedding(f"{subject} {body}")
            email_id = str(uuid.uuid4())
            await pinecone_service.upsert_email_embedding(
                email_id=email_id,
                embedding=embedding,
                metadata={
                    "subject": subject,
                    "sender": sender,
                    "priority_score": analysis["priority_score"],
                    "priority_level": analysis["priority_level"],
                    "intent": analysis["intent"],
                    "received_at": received_at.isoformat(),
                },
            )
            latency_ms = (time.time() - start) * 1000
            metrics.record_email_processing(latency_ms, success=True)
            results.append({
                "email_id": email_id,
                "priority_score": analysis["priority_score"],
                "priority_level": analysis["priority_level"],
                "intent": analysis["intent"],
                "sentiment": analysis["sentiment"],
                "urgency_keywords": analysis.get("urgency_keywords") or [],
                "sender_importance": analysis.get("sender_importance", 0.5),
                "processing_time_ms": latency_ms,
                "subject": subject,
                "sender": sender,
            })
        except Exception as e:
            print(f"Error processing email: {e}")
            continue

    return {"results": results, "total": len(results)}


@router.get("/{email_id}", response_model=Email)
async def get_email(email_id: str):
    supabase_client = SupabaseClient()
    supabase_client.initialize()
    email_data = await supabase_client.get_email(email_id)
    if not email_data:
        raise HTTPException(status_code=404, detail="Email not found")
    return email_data


@router.get("/user/{user_id}/emails")
async def get_user_emails(
    user_id: str,
    limit: int = 50,
    offset: int = 0,
    priority_level: Optional[str] = None
):
    supabase_client = SupabaseClient()
    supabase_client.initialize()
    emails = await supabase_client.get_user_emails(
        user_id=user_id,
        limit=limit,
        offset=offset,
        priority_level=priority_level
    )
    return {"emails": emails, "count": len(emails)}
