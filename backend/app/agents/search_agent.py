"""
Search Agent
Fetches relevant information for research sections
Pure function using public APIs (no authentication needed)
"""
import logging
import httpx
from typing import List, Dict, Any
import asyncio

logger = logging.getLogger(__name__)


async def search_for_section(section_title: str, topic: str) -> str:
    """
    Fetch relevant information for a research section
    Uses Wikipedia API (free, no auth required, no rate limits)
    
    Args:
        section_title: Title of the research section (e.g., "Introduction to AI")
        topic: Main research topic (e.g., "Artificial Intelligence")
    
    Returns:
        str: Raw text content relevant to the section
    
    Raises:
        Exception: If search fails (returns empty string instead)
    
    Example:
        >>> content = await search_for_section("Key Concepts", "Machine Learning")
        >>> len(content) > 0
        True
    """
    
    # Use topic as primary search query
    search_query = topic
    
    try:
        logger.info(f"Searching for: {search_query} (section: {section_title})")
        
        # Try Wikipedia first (most reliable for academic topics)
        content = await _search_wikipedia(search_query)
        
        if content and len(content) > 100:
            logger.info(f"Found {len(content)} chars from Wikipedia")
            return content
        
        # Fallback: return structured placeholder
        logger.warning(f"Limited content found, using structured placeholder")
        return _create_placeholder_content(topic, section_title)
        
    except Exception as e:
        logger.error(f"Search agent failed: {e}")
        # Return placeholder instead of raising (graceful degradation)
        return _create_placeholder_content(topic, section_title)


async def _search_wikipedia(query: str) -> str:
    """
    Search Wikipedia for relevant content
    Public API, no authentication required
    
    Args:
        query: Search query
    
    Returns:
        str: Wikipedia article content or empty string
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Wikipedia search API
            params = {
                "action": "query",
                "format": "json",
                "titles": query,
                "prop": "extracts",
                "explaintext": True,
                "exintro": False,
                "exlimit": 1
            }
            
            response = await client.get(
                "https://en.wikipedia.org/w/api.php",
                params=params
            )
            
            if response.status_code != 200:
                logger.warning(f"Wikipedia API returned {response.status_code}")
                return ""
            
            data = response.json()
            
            # Extract page content
            pages = data.get("query", {}).get("pages", {})
            if not pages:
                logger.warning("No Wikipedia pages found")
                return ""
            
            # Get first (usually only) page
            page = next(iter(pages.values()))
            content = page.get("extract", "")
            
            # Limit to first 2000 chars to keep focused
            return content[:2000] if content else ""
            
    except httpx.TimeoutException:
        logger.warning("Wikipedia search timed out")
        return ""
    except Exception as e:
        logger.error(f"Wikipedia search error: {e}")
        return ""


def _create_placeholder_content(topic: str, section: str) -> str:
    """
    Create structured placeholder content when search fails
    Allows agents to continue processing
    
    Args:
        topic: Main research topic
        section: Section title
    
    Returns:
        str: Placeholder content
    """
    return f"""
Content for {section} in {topic}:

This section covers the key aspects of {section.lower()} as it relates to {topic}.
Research on this topic indicates several important points:

1. Foundational concepts and definitions relevant to this section
2. Historical development and evolution of ideas in this area
3. Current state of knowledge and recent developments
4. Important contributions from researchers and practitioners
5. Practical applications and real-world examples

[This is placeholder content. In production, this would be populated with actual 
research data from academic sources, Wikipedia, or other knowledge bases.]
"""
