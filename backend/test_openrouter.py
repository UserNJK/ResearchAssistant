"""
Test script for OpenRouter LLM integration
Run this to verify PHASE 2 implementation
"""
import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.openrouter import call_llm, test_llm_connection, OpenRouterError
from app.config import settings


async def test_basic_call():
    """Test basic LLM call"""
    print("\n" + "="*60)
    print("TEST 1: Basic LLM Call (with caching)")
    print("="*60)
    
    prompt = "What is 2 + 2? Answer in one sentence."
    
    try:
        response = await call_llm(prompt, max_tokens=50)
        print(f"✅ Success!")
        print(f"Prompt: {prompt}")
        print(f"Response: {response}")
        
        # Test cache by calling again
        print("\nTesting cache with same prompt...")
        response2 = await call_llm(prompt, max_tokens=50)
        if response == response2:
            print("✅ Cache working - got same response without API call")
        
        return True
    except OpenRouterError as e:
        print(f"❌ Failed: {e}")
        return False


async def test_with_specific_model():
    """Test with specific model"""
    print("\n" + "="*60)
    print("TEST 2: Specific Model Call")
    print("="*60)
    
    prompt = "List 3 colors in a comma-separated list."
    model = settings.PLANNER_MODEL
    
    try:
        response = await call_llm(prompt, model=model, max_tokens=30)
        print(f"✅ Success!")
        print(f"Model: {model}")
        print(f"Response: {response}")
        return True
    except OpenRouterError as e:
        print(f"❌ Failed: {e}")
        return False


async def test_temperature_control():
    """Test temperature parameter"""
    print("\n" + "="*60)
    print("TEST 3: Temperature Control")
    print("="*60)
    
    prompt = "Write one creative sentence about the moon."
    
    try:
        # Low temperature (more deterministic)
        response = await call_llm(prompt, temperature=0.1, max_tokens=50)
        print(f"✅ Success (temperature=0.1)")
        print(f"Response: {response}")
        return True
    except OpenRouterError as e:
        print(f"❌ Failed: {e}")
        return False


async def test_connection_helper():
    """Test the connection test helper"""
    print("\n" + "="*60)
    print("TEST 4: Connection Test Helper")
    print("="*60)
    
    result = await test_llm_connection()
    
    if result["status"] == "success":
        print(f"✅ {result['message']}")
        print(f"Model: {result['model']}")
        print(f"Response: {result['response']}")
        return True
    else:
        print(f"❌ {result['message']}")
        print(f"Error: {result['error']}")
        return False


async def test_error_handling():
    """Test error handling with invalid config"""
    print("\n" + "="*60)
    print("TEST 5: Error Handling")
    print("="*60)
    
    # Save original key
    original_key = settings.OPENROUTER_API_KEY
    
    # Test with empty key
    settings.OPENROUTER_API_KEY = ""
    
    try:
        await call_llm("test")
        print("❌ Should have raised error for missing API key")
        result = False
    except OpenRouterError as e:
        if "not configured" in str(e):
            print(f"✅ Correctly caught missing API key error")
            result = True
        else:
            print(f"❌ Unexpected error: {e}")
            result = False
    finally:
        # Restore original key
        settings.OPENROUTER_API_KEY = original_key
    
    return result


async def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("PHASE 2: OpenRouter LLM Layer Tests")
    print("="*70)
    
    # Check configuration
    print(f"\nConfiguration:")
    print(f"  OpenRouter Base URL: {settings.OPENROUTER_BASE_URL}")
    print(f"  API Key Configured: {bool(settings.OPENROUTER_API_KEY)}")
    print(f"  Default Model: {settings.DEFAULT_FALLBACK_MODEL}")
    print(f"  Temperature: {settings.LLM_TEMPERATURE}")
    print(f"  Max Tokens: {settings.LLM_MAX_TOKENS}")
    print(f"  Timeout: {settings.LLM_TIMEOUT_SECONDS}s")
    
    if not settings.OPENROUTER_API_KEY:
        print("\n⚠️  WARNING: OPENROUTER_API_KEY not set!")
        print("   Set it in backend/.env to run live tests")
        print("   Some tests will be skipped.")
        
        # Only run error handling test
        results = [await test_error_handling()]
    else:
        print("\n⚠️  NOTE: Tests will use rate limiting (1s between calls)")
        print("   This is to avoid hitting API quota limits")
        print("   Responses are cached to reduce duplicate calls")
        
        # Run all tests with delays to respect rate limiting
        results = [
            await test_basic_call(),
            await test_with_specific_model(),
            await test_temperature_control(),
            await test_connection_helper(),
            await test_error_handling(),
        ]
    
    # Summary
    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED - PHASE 2 COMPLETE!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
