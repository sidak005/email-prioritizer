#!/usr/bin/env python3
"""
Email Prioritizer - Run Script
Start the server with: python3 run.py
"""

if __name__ == "__main__":
    print("🔧 Loading uvicorn...")
    try:
        import uvicorn
        print("✅ Uvicorn loaded")
    except ImportError:
        print("❌ uvicorn not installed. Installing...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "uvicorn[standard]"])
        import uvicorn
    
    print("📦 Importing app...")
    try:
        from backend.app.main import app
        print("✅ App imported successfully")
    except Exception as e:
        print(f"❌ Failed to import app: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
    
    print("🚀 Starting server...")
    print("📡 Server will be available at http://localhost:8000")
    print("📚 API docs will be available at http://localhost:8000/docs")
    
    uvicorn.run(
        app,  # Pass app object directly instead of string
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disabled to avoid watching venv directory
        log_level="info",
    )
