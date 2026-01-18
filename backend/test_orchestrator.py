"""
PHASE 4: Orchestrator Test Suite
Tests for the research orchestration pipeline with job tracking.

Run with: python test_orchestrator.py
"""

import asyncio
import logging
from datetime import datetime

from app.orchestrator import (
    orchestrate_research,
    create_job,
    get_job,
    list_jobs,
    cancel_job,
    clear_all_jobs,
    get_job_stats,
    JobStatus,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_basic_orchestration():
    """TEST 1: Basic research orchestration pipeline."""
    print("\n" + "="*70)
    print("TEST 1: Basic Research Orchestration")
    print("="*70)

    clear_all_jobs()

    topic = "Quantum Computing"
    print(f"\n📚 Starting research orchestration for: {topic}")

    try:
        job = await orchestrate_research(topic)

        print(f"\n✅ Orchestration completed successfully")
        print(f"   Job ID: {job.job_id}")
        print(f"   Status: {job.status.value}")
        print(f"   Sections planned: {job.progress.get('total_sections', 0)}")

        if job.status == JobStatus.COMPLETE:
            result = job.result
            print(f"\n✅ Result obtained:")
            print(f"   - {len(result['sections'])} sections")
            print(f"   - {len(result['summaries'])} summaries")
            print(f"   - Insights: {len(result['insights'].get('trends', []))} trends, "
                  f"{len(result['insights'].get('gaps', []))} gaps")
            print(f"   - Final paper length: {len(result['final_paper'])} chars")
            return True

        else:
            print(f"❌ Orchestration failed: {job.error}")
            return False

    except Exception as e:
        print(f"❌ Exception during orchestration: {str(e)}")
        return False


async def test_job_status_tracking():
    """TEST 2: Job creation and status tracking."""
    print("\n" + "="*70)
    print("TEST 2: Job Status Tracking")
    print("="*70)

    clear_all_jobs()

    print("\n📋 Creating new job...")
    job = create_job("Machine Learning")
    print(f"✅ Job created: {job.job_id}")
    print(f"   Initial status: {job.status.value}")
    print(f"   Topic: {job.topic}")

    print("\n🔍 Retrieving job...")
    retrieved = get_job(job.job_id)
    if retrieved and retrieved.job_id == job.job_id:
        print(f"✅ Job retrieved successfully")
        return True
    else:
        print(f"❌ Failed to retrieve job")
        return False


async def test_multi_job_orchestration():
    """TEST 3: Multiple concurrent jobs."""
    print("\n" + "="*70)
    print("TEST 3: Multi-Job Orchestration (Concurrent)")
    print("="*70)

    clear_all_jobs()

    topics = ["Neural Networks", "Blockchain Technology"]
    print(f"\n🚀 Starting {len(topics)} concurrent research jobs...")

    try:
        # Run multiple orchestrations concurrently
        jobs = await asyncio.gather(
            *[orchestrate_research(topic) for topic in topics],
            return_exceptions=True
        )

        successful = sum(1 for j in jobs if isinstance(j, type(jobs[0])) and j.status == JobStatus.COMPLETE)
        print(f"\n✅ Completed {successful}/{len(topics)} jobs")

        for i, job in enumerate(jobs):
            if isinstance(job, Exception):
                print(f"   Job {i+1}: ❌ Exception: {str(job)}")
            else:
                print(f"   Job {i+1}: {job.topic} - {job.status.value}")

        return successful > 0

    except Exception as e:
        print(f"❌ Error during concurrent orchestration: {str(e)}")
        return False


async def test_job_listing_and_stats():
    """TEST 4: Job listing and statistics."""
    print("\n" + "="*70)
    print("TEST 4: Job Listing and Statistics")
    print("="*70)

    clear_all_jobs()

    print("\n📊 Creating sample jobs...")
    job1 = create_job("Artificial Intelligence")
    job2 = create_job("Genetic Algorithms")
    job3 = create_job("Deep Learning")

    print(f"✅ Created 3 jobs")

    print("\n📋 Listing all jobs...")
    all_jobs = list_jobs()
    print(f"✅ Total jobs: {len(all_jobs)}")
    for j in all_jobs:
        print(f"   - {j.job_id}: {j.topic}")

    print("\n🔎 Filtering jobs by topic...")
    ai_jobs = list_jobs(topic="Artificial Intelligence")
    print(f"✅ Found {len(ai_jobs)} job(s) matching 'Artificial Intelligence'")

    print("\n📈 Getting job statistics...")
    stats = get_job_stats()
    print(f"✅ Statistics:")
    print(f"   - Total jobs: {stats['total_jobs']}")
    print(f"   - By status: {stats['by_status']}")

    return len(all_jobs) == 3 and len(ai_jobs) == 1


async def test_job_cancellation():
    """TEST 5: Job cancellation."""
    print("\n" + "="*70)
    print("TEST 5: Job Cancellation")
    print("="*70)

    clear_all_jobs()

    print("\n📋 Creating a pending job...")
    job = create_job("Natural Language Processing")
    print(f"✅ Job created: {job.job_id}")
    print(f"   Status: {job.status.value}")

    print("\n❌ Cancelling job...")
    cancelled = cancel_job(job.job_id)
    print(f"✅ Job cancelled")
    print(f"   Status: {cancelled.status.value}")
    print(f"   Error: {cancelled.error}")

    if cancelled.status == JobStatus.ERROR:
        print("\n✅ Job successfully marked as cancelled")
        return True
    else:
        print("\n❌ Job cancellation failed")
        return False


async def test_error_recovery():
    """TEST 6: Graceful error handling in orchestration."""
    print("\n" + "="*70)
    print("TEST 6: Error Handling and Recovery")
    print("="*70)

    clear_all_jobs()

    print("\n⚠️ Testing invalid input...")
    try:
        await orchestrate_research("")
        print("❌ Should have raised ValueError for empty topic")
        return False
    except ValueError as e:
        print(f"✅ Correctly raised ValueError: {str(e)}")

    print("\n⚠️ Testing invalid job retrieval...")
    try:
        await orchestrate_research("AI Research", job_id="invalid-id")
        print("❌ Should have raised ValueError for invalid job ID")
        return False
    except ValueError as e:
        print(f"✅ Correctly raised ValueError: {str(e)}")

    print("\n✅ Error handling test passed")
    return True


async def run_all_tests():
    """Run complete test suite."""
    print("\n" + "█"*70)
    print("█ PHASE 4: ORCHESTRATOR TEST SUITE")
    print("█"*70)

    tests = [
        ("Basic Orchestration", test_basic_orchestration),
        ("Job Status Tracking", test_job_status_tracking),
        ("Multi-Job Orchestration", test_multi_job_orchestration),
        ("Job Listing & Stats", test_job_listing_and_stats),
        ("Job Cancellation", test_job_cancellation),
        ("Error Handling", test_error_recovery),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"Test '{name}' failed with exception: {str(e)}", exc_info=True)
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
        print("\n✅ ALL ORCHESTRATOR TESTS PASSED - PHASE 4 READY! 🎉")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")

    clear_all_jobs()
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
