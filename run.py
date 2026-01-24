#!/usr/bin/env python3
"""
Email Prioritizer - Run Script
Start the server with: python3 run.py
"""

if __name__ == "__main__":
    try:
        import uvicorn
    except ImportError:
        print("❌ uvicorn not installed. Installing...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "uvicorn[standard]"])
        import uvicorn
    
    from pathlib import Path
    
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        reload_dirs=[Path("backend")],  # Only watch backend directory, ignore venv
    )
