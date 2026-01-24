#!/usr/bin/env python3
"""Quick test to see if backend can start"""

import sys
print("Step 1: Importing...")
sys.stdout.flush()

try:
    from backend.app.main import app
    print("✅ App imported")
    sys.stdout.flush()
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("Step 2: Testing app...")
sys.stdout.flush()

# Test if we can access the app
print(f"✅ App type: {type(app)}")
print(f"✅ App title: {app.title}")
sys.stdout.flush()

print("Step 3: Starting uvicorn...")
sys.stdout.flush()

import uvicorn
print("✅ Uvicorn imported")
sys.stdout.flush()

print("🚀 Calling uvicorn.run()...")
sys.stdout.flush()

uvicorn.run(
    app,
    host="127.0.0.1",  # Use localhost instead of 0.0.0.0
    port=8000,
    reload=False,
    log_level="debug",  # More verbose
)
