from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time

from backend.app.config import settings
from backend.app.api.routes import emails, priority, responses
from backend.app.utils.metrics import MetricsCollector

# Initialize metrics collector
metrics = MetricsCollector()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Email Prioritizer API...")
    try:
        print(f"Environment: {settings.environment}")
    except Exception as e:
        print(f"⚠️ Config error: {e}")
    
    # Initialize services (store in app state for access in routes)
    from backend.app.services.pinecone_service import PineconeService
    from backend.app.services.llm_service import LLMService
    from backend.app.services.embedding_service import EmbeddingService
    from backend.app.database.supabase_client import SupabaseClient
    
    # Initialize Supabase (optional - server can run without it)
    try:
        supabase_client = SupabaseClient()
        supabase_client.initialize()
        app.state.supabase = supabase_client
        print("✅ Supabase initialized")
    except Exception as e:
        print(f"⚠️ Supabase initialization failed: {e}")
        print("⚠️ Server will continue without Supabase - some features disabled")
        app.state.supabase = None
    
    # Initialize Embedding Service
    try:
        embedding_service = EmbeddingService()
        await embedding_service.initialize()
        app.state.embedding = embedding_service
        print("✅ Embedding service initialized")
    except Exception as e:
        print(f"⚠️ Embedding service initialization failed: {e}")
        print("⚠️ Server will continue - embeddings will use HF API")
        app.state.embedding = None
    
    # Initialize Pinecone (optional - server can run without it)
    try:
        pinecone_service = PineconeService()
        await pinecone_service.initialize()
        app.state.pinecone = pinecone_service
        print("✅ Pinecone initialized")
    except Exception as e:
        print(f"⚠️ Pinecone initialization failed: {e}")
        print("⚠️ Server will continue without Pinecone - some features disabled")
        app.state.pinecone = None
    
    # Initialize LLM (load models)
    try:
        llm_service = LLMService()
        await llm_service.initialize()
        app.state.llm = llm_service
        print("✅ LLM service initialized")
    except Exception as e:
        print(f"⚠️ LLM service initialization failed: {e}")
        print("⚠️ Server will continue - LLM will use HF API")
        app.state.llm = None
    
    print("✅ Services initialized (some may be disabled)")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down...")


app = FastAPI(
    title="Email Prioritizer API",
    description="AI-powered email prioritization and response generation",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(emails.router, prefix="/api/v1/emails", tags=["emails"])
app.include_router(priority.router, prefix="/api/v1/priority", tags=["priority"])
app.include_router(responses.router, prefix="/api/v1/responses", tags=["responses"])


@app.get("/")
async def root():
    return {
        "message": "Email Prioritizer API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time()
    }


@app.get("/metrics")
async def get_metrics():
    """Get performance metrics"""
    return metrics.get_metrics()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
