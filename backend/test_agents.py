"""
Test suite for PHASE 3 Agent implementations
Tests pure functions in isolation
"""
import asyncio
import sys
import os
from typing import List

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.planner import plan_research, _parse_section_titles
from agents.search_agent import search_for_section
from agents.summarizer import summarize_content
from agents.insight_agent import extract_insights
from agents.formatter import format_section


async def test_planner():
    """Test planner agent"""
    print("\n" + "="*60)
    print("TEST 1: Planner Agent")
    print("="*60)
    
    try:
        sections = await plan_research("Quantum Computing", max_sections=3)
        print(f"✅ Generated {len(sections)} sections:")
        for i, section in enumerate(sections, 1):
            print(f"   {i}. {section}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


async def test_search():
    """Test search agent"""
    print("\n" + "="*60)
    print("TEST 2: Search Agent")
    print("="*60)
    
    try:
        content = await search_for_section("Introduction", "Quantum Computing")
        print(f"✅ Retrieved content: {len(content)} chars")
        print(f"   Preview: {content[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


async def test_summarizer():
    """Test summarization agent"""
    print("\n" + "="*60)
    print("TEST 3: Summarization Agent")
    print("="*60)
    
    test_content = """
    Quantum computing is a revolutionary field that leverages quantum mechanics 
    to process information in fundamentally different ways than classical computers. 
    Key concepts include quantum bits (qubits), superposition, and entanglement.
    """
    
    try:
        summary = await summarize_content(test_content, "Introduction", max_length=100)
        print(f"✅ Generated summary: {len(summary)} chars")
        print(f"   Summary: {summary[:150]}...")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


async def test_insight_extractor():
    """Test insight agent"""
    print("\n" + "="*60)
    print("TEST 4: Insight Agent")
    print("="*60)
    
    test_summaries = {
        "Introduction": "Overview of quantum computing and its importance",
        "Key Concepts": "Qubits, superposition, entanglement and quantum gates",
        "Applications": "Quantum computing uses in cryptography and optimization"
    }
    
    try:
        insights = await extract_insights(test_summaries, "Quantum Computing")
        print(f"✅ Extracted insights:")
        print(f"   Trends: {len(insights['trends'])} items")
        print(f"   Gaps: {len(insights['gaps'])} items")
        print(f"   Conclusions: {len(insights['conclusions'])} items")
        
        if insights['trends']:
            print(f"   Sample trend: {insights['trends'][0]}")
        
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


async def test_formatter():
    """Test formatting agent"""
    print("\n" + "="*60)
    print("TEST 5: Formatting Agent")
    print("="*60)
    
    test_section = "This is introduction content about quantum computing"
    
    try:
        formatted = await format_section("Introduction", test_section, 1)
        print(f"✅ Formatted section: {len(formatted)} chars")
        print(f"   Preview: {formatted[:150]}...")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_parsing():
    """Test parsing functions (no async needed)"""
    print("\n" + "="*60)
    print("TEST 6: Parsing Functions")
    print("="*60)
    
    test_response = """
1. Introduction to Machine Learning
2. Supervised Learning Techniques
3. Unsupervised Learning Methods
4. Deep Learning and Neural Networks
5. Applications and Future Trends
"""
    
    sections = _parse_section_titles(test_response)
    
    if len(sections) >= 3:
        print(f"✅ Parsed {len(sections)} sections:")
        for section in sections:
            print(f"   - {section}")
        return True
    else:
        print(f"❌ Failed to parse sections")
        return False


async def run_all_tests():
    """Run all agent tests"""
    print("\n" + "="*70)
    print("PHASE 3: Agent Implementation Tests")
    print("="*70)
    
    print("\nConfiguration:")
    print("  - Agents are pure functions")
    print("  - No side effects beyond logging")
    print("  - Use existing call_llm() wrapper")
    print("  - Deterministic and testable")
    
    # Run async tests
    async_results = [
        await test_planner(),
        await test_search(),
        await test_summarizer(),
        await test_insight_extractor(),
        await test_formatter(),
    ]
    
    # Run sync tests
    sync_results = [
        test_parsing(),
    ]
    
    all_results = async_results + sync_results
    
    # Summary
    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)
    
    passed = sum(all_results)
    total = len(all_results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL AGENT TESTS PASSED - PHASE 3 COMPLETE!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) encountered issues")
        print("   (This is expected if OpenRouter quota is exceeded)")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
