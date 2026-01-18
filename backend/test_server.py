"""Test script to verify the FastAPI server"""
import httpx
import sys

def test_health_endpoint():
    """Test the /health endpoint"""
    try:
        response = httpx.get("http://127.0.0.1:8000/health", timeout=5.0)
        print(f"Status Code: {response.status_code}")
        print(f"Response JSON: {response.json()}")
        
        if response.status_code == 200:
            print("\n✅ PHASE 1 VERIFICATION SUCCESSFUL!")
            print("Backend is running and healthy.")
            return 0
        else:
            print(f"\n❌ Unexpected status code: {response.status_code}")
            return 1
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        print("Make sure the server is running: python -m uvicorn app.main:app --reload")
        return 1

def test_root_endpoint():
    """Test the root endpoint"""
    try:
        response = httpx.get("http://127.0.0.1:8000/", timeout=5.0)
        print(f"\nRoot endpoint status: {response.status_code}")
        print(f"Root response: {response.json()}")
        return 0
    except Exception as e:
        print(f"Error testing root: {e}")
        return 1

if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 1 Backend Verification Test")
    print("=" * 60)
    
    result1 = test_health_endpoint()
    result2 = test_root_endpoint()
    
    sys.exit(max(result1, result2))
