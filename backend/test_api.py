"""
PHASE 5: API Endpoint Tests
Tests for research API endpoints with background tasks.

Run with: python test_api.py
"""

import asyncio
import logging
from httpx import AsyncClient
from app.main import app
from app.orchestrator import clear_all_jobs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_health_check():
    """TEST 1: Health check endpoint"""
    print("\n" + "="*70)
    print("TEST 1: Health Check Endpoint")
    print("="*70)

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        
        print(f"\n✅ Health check successful")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        return True


async def test_start_research():
    """TEST 2: Start new research job"""
    print("\n" + "="*70)
    print("TEST 2: Start New Research Job")
    print("="*70)

    clear_all_jobs()

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/research",
            json={"topic": "Artificial Intelligence"}
        )
        
        print(f"\n✅ Job created successfully")
        print(f"   Status code: {response.status_code}")
        
        assert response.status_code == 200
        data = response.json()
        print(f"   Job ID: {data['job_id']}")
        print(f"   Topic: {data['topic']}")
        print(f"   Status: {data['status']}")
        
        assert data["topic"] == "Artificial Intelligence"
        assert data["status"] == "pending"
        
        return data["job_id"]


async def test_get_job_status():
    """TEST 3: Get job status"""
    print("\n" + "="*70)
    print("TEST 3: Get Job Status")
    print("="*70)

    clear_all_jobs()

    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create job
        create_response = await client.post(
            "/api/research",
            json={"topic": "Machine Learning"}
        )
        job_id = create_response.json()["job_id"]
        
        # Get status
        status_response = await client.get(f"/api/research/{job_id}")
        
        print(f"\n✅ Job status retrieved")
        print(f"   Job ID: {job_id}")
        print(f"   Status code: {status_response.status_code}")
        
        assert status_response.status_code == 200
        data = status_response.json()
        print(f"   Status: {data['status']}")
        print(f"   Progress: {data['progress']}")
        
        return True


async def test_job_not_found():
    """TEST 4: 404 for non-existent job"""
    print("\n" + "="*70)
    print("TEST 4: 404 for Non-Existent Job")
    print("="*70)

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/research/invalid-job-id")
        
        print(f"\n✅ Correctly returned 404")
        print(f"   Status code: {response.status_code}")
        print(f"   Error: {response.json()}")
        
        assert response.status_code == 404
        return True


async def test_list_jobs():
    """TEST 5: List all research jobs"""
    print("\n" + "="*70)
    print("TEST 5: List All Research Jobs")
    print("="*70)

    clear_all_jobs()

    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create multiple jobs
        topics = ["AI", "Machine Learning", "Deep Learning"]
        for topic in topics:
            await client.post(
                "/api/research",
                json={"topic": topic}
            )
        
        # List all
        response = await client.get("/api/research")
        
        print(f"\n✅ Retrieved job list")
        print(f"   Status code: {response.status_code}")
        
        assert response.status_code == 200
        jobs = response.json()
        print(f"   Total jobs: {len(jobs)}")
        
        for job in jobs:
            print(f"   - {job['job_id']}: {job['topic']}")
        
        assert len(jobs) == 3
        return True


async def test_list_jobs_filtered():
    """TEST 6: List jobs with topic filter"""
    print("\n" + "="*70)
    print("TEST 6: List Jobs with Topic Filter")
    print("="*70)

    clear_all_jobs()

    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create jobs
        topics = ["AI", "Blockchain", "AI"]
        for topic in topics:
            await client.post(
                "/api/research",
                json={"topic": topic}
            )
        
        # Filter by topic
        response = await client.get("/api/research?topic=AI")
        
        print(f"\n✅ Retrieved filtered job list")
        print(f"   Filter: topic=AI")
        
        assert response.status_code == 200
        jobs = response.json()
        print(f"   Matching jobs: {len(jobs)}")
        
        assert len(jobs) == 2
        assert all(j["topic"] == "AI" for j in jobs)
        return True


async def test_empty_topic_error():
    """TEST 7: 400 for empty topic"""
    print("\n" + "="*70)
    print("TEST 7: 400 for Empty Topic")
    print("="*70)

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/research",
            json={"topic": ""}
        )
        
        print(f"\n✅ Correctly returned 400")
        print(f"   Status code: {response.status_code}")
        print(f"   Error: {response.json()}")
        
        assert response.status_code == 400
        return True


async def test_cancel_job():
    """TEST 8: Cancel a pending job"""
    print("\n" + "="*70)
    print("TEST 8: Cancel Pending Job")
    print("="*70)

    clear_all_jobs()

    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create job
        create_response = await client.post(
            "/api/research",
            json={"topic": "Quantum Computing"}
        )
        job_id = create_response.json()["job_id"]
        
        # Cancel job
        cancel_response = await client.post(f"/api/research/{job_id}/cancel")
        
        print(f"\n✅ Job cancelled successfully")
        print(f"   Job ID: {job_id}")
        print(f"   Status code: {cancel_response.status_code}")
        
        assert cancel_response.status_code == 200
        data = cancel_response.json()
        assert data["status"] == "error"
        print(f"   New status: {data['status']}")
        print(f"   Error: {data['error']}")
        
        return True


async def test_get_stats():
    """TEST 9: Get job statistics"""
    print("\n" + "="*70)
    print("TEST 9: Get Job Statistics")
    print("="*70)

    clear_all_jobs()

    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create a few jobs
        for i in range(3):
            await client.post(
                "/api/research",
                json={"topic": f"Topic {i}"}
            )
        
        # Get stats
        response = await client.get("/api/research/stats")
        
        print(f"\n✅ Retrieved statistics")
        print(f"   Status code: {response.status_code}")
        
        assert response.status_code == 200
        stats = response.json()
        print(f"   Total jobs: {stats['total_jobs']}")
        print(f"   By status: {stats['by_status']}")
        
        assert stats["total_jobs"] == 3
        return True


async def test_llm_endpoints():
    """TEST 10: LLM test endpoints"""
    print("\n" + "="*70)
    print("TEST 10: LLM Test Endpoints")
    print("="*70)

    async with AsyncClient(app=app, base_url="http://test") as client:
        # Test cache stats
        stats_response = await client.get("/llm-stats")
        print(f"\n✅ LLM stats retrieved")
        print(f"   Status: {stats_response.status_code}")
        assert stats_response.status_code == 200
        
        # Clear cache
        clear_response = await client.post("/llm-cache/clear")
        print(f"\n✅ LLM cache cleared")
        print(f"   Status: {clear_response.status_code}")
        assert clear_response.status_code == 200
        
        return True


async def run_all_tests():
    """Run complete test suite"""
    print("\n" + "█"*70)
    print("█ PHASE 5: API ENDPOINT TEST SUITE")
    print("█"*70)

    tests = [
        ("Health Check", test_health_check),
        ("Start Research", test_start_research),
        ("Get Job Status", test_get_job_status),
        ("Job Not Found", test_job_not_found),
        ("List All Jobs", test_list_jobs),
        ("List Jobs Filtered", test_list_jobs_filtered),
        ("Empty Topic Error", test_empty_topic_error),
        ("Cancel Job", test_cancel_job),
        ("Job Statistics", test_get_stats),
        ("LLM Endpoints", test_llm_endpoints),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result if isinstance(result, bool) else True))
        except Exception as e:
            logger.error(f"Test '{name}' failed: {str(e)}", exc_info=True)
            results.append((name, False))

    # Summary
    print("\n" + "█"*70)
    print("█ TEST SUMMARY")
    print("█"*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print(f"\n📊 Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n✅ ALL API TESTS PASSED - PHASE 5 READY! 🎉")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")

    clear_all_jobs()
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
