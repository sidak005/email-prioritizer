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
    
    # Initialize services lazily (store in app state for access in routes)
    # Don't initialize all services at startup to avoid blocking
    print("📦 Services will be initialized on first use...")
    
    app.state.supabase = None
    app.state.embedding = None
    app.state.pinecone = None
    app.state.llm = None
    
    print("✅ FastAPI app ready - services initialized lazily")
    
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
