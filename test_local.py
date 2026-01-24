#!/usr/bin/env python3
"""
Local Testing Script - Test all features before deployment
"""

import requests
import json
from datetime import datetime

API_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_test(name):
    print(f"\n✓ Testing: {name}")

def test_backend_health():
    """Test 1: Backend health check"""
    print_test("Backend Health Check")
    try:
        r = requests.get(f"{API_URL}/health", timeout=5)
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "healthy"
        print(f"  ✅ Backend is healthy: {data}")
        return True
    except Exception as e:
        print(f"  ❌ Backend health check failed: {e}")
        return False

def test_analyze_email():
    """Test 2: Analyze email endpoint"""
    print_test("Analyze Email")
    try:
        payload = {
            "subject": "URGENT: Server down - immediate action needed!",
            "sender": "cto@company.com",
            "recipient": "you@company.com",
            "body": "The production server crashed. We need you to fix this immediately. This is critical!",
            "received_at": datetime.now().isoformat()
        }
        r = requests.post(f"{API_URL}/api/v1/emails/analyze", json=payload, timeout=30)
        assert r.status_code == 200
        data = r.json()
        assert "priority_score" in data
        assert "priority_level" in data
        assert data["priority_level"] in ["urgent", "high", "normal", "low", "spam"]
        print(f"  ✅ Email analyzed successfully!")
        print(f"     Priority: {data['priority_level']} ({data['priority_score']:.1f}/100)")
        print(f"     Intent: {data['intent']}, Sentiment: {data['sentiment']}")
        return True
    except Exception as e:
        print(f"  ❌ Analyze email failed: {e}")
        return False

def test_generate_response():
    """Test 3: Generate response endpoint"""
    print_test("Generate Response")
    try:
        payload = {
            "email_subject": "Can we schedule a meeting tomorrow?",
            "email_body": "Hi, I would like to schedule a meeting for tomorrow afternoon if you are available.",
            "tone": "professional"
        }
        r = requests.post(f"{API_URL}/api/v1/responses/generate", json=payload, timeout=30)
        assert r.status_code == 200
        data = r.json()
        assert "generated_response" in data
        assert "tone" in data
        print(f"  ✅ Response generated successfully!")
        print(f"     Tone: {data['tone']}")
        print(f"     Response: {data['generated_response'][:80]}...")
        return True
    except Exception as e:
        print(f"  ❌ Generate response failed: {e}")
        return False

def test_fetch_inbox_endpoint():
    """Test 4: Fetch inbox endpoint (with invalid creds - should return 400)"""
    print_test("Fetch Inbox Endpoint (Invalid Credentials)")
    try:
        payload = {
            "email": "test@gmail.com",
            "password": "wrong_password",
            "limit": 5
        }
        r = requests.post(f"{API_URL}/api/v1/emails/fetch", json=payload, timeout=10)
        # Should return 400 (bad request) for invalid credentials
        assert r.status_code == 400
        print(f"  ✅ Endpoint exists and validates credentials correctly")
        print(f"     Error message: {r.json().get('detail', 'N/A')[:60]}...")
        return True
    except Exception as e:
        print(f"  ❌ Fetch inbox endpoint test failed: {e}")
        return False

def test_frontend_connection():
    """Test 5: Frontend can connect to backend"""
    print_test("Frontend → Backend Connection")
    try:
        # Test if frontend is running
        r = requests.get(FRONTEND_URL, timeout=5)
        assert r.status_code == 200
        print(f"  ✅ Frontend is running at {FRONTEND_URL}")
        
        # Test if frontend can reach backend (via API call from frontend's perspective)
        # We'll just verify the frontend page loads - actual API calls happen in browser
        print(f"  ✅ Frontend should be able to call backend at {API_URL}")
        print(f"     Open {FRONTEND_URL} in your browser to test the UI")
        return True
    except Exception as e:
        print(f"  ❌ Frontend connection test failed: {e}")
        print(f"     Make sure frontend is running: cd frontend && npm run dev")
        return False

def test_api_docs():
    """Test 6: API documentation endpoint"""
    print_test("API Documentation")
    try:
        r = requests.get(f"{API_URL}/docs", timeout=5)
        assert r.status_code == 200
        print(f"  ✅ API docs available at {API_URL}/docs")
        return True
    except Exception as e:
        print(f"  ❌ API docs check failed: {e}")
        return False

def main():
    print_header("🧪 Local Testing - Email Prioritizer")
    print("\nTesting all features before deployment...")
    print(f"Backend: {API_URL}")
    print(f"Frontend: {FRONTEND_URL}")
    
    results = []
    
    results.append(("Backend Health", test_backend_health()))
    results.append(("Analyze Email", test_analyze_email()))
    results.append(("Generate Response", test_generate_response()))
    results.append(("Fetch Inbox Endpoint", test_fetch_inbox_endpoint()))
    results.append(("Frontend Connection", test_frontend_connection()))
    results.append(("API Documentation", test_api_docs()))
    
    print_header("📊 Test Results Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Ready for deployment!")
        print("\n📝 Next steps:")
        print("   1. Open frontend in browser: http://localhost:3000")
        print("   2. Test the UI: Analyze email, Connect inbox, Generate response")
        print("   3. Once UI works, follow DEPLOY_RAILWAY_VERCEL.md")
    else:
        print("\n⚠️  Some tests failed. Fix issues before deploying.")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test script error: {e}")
