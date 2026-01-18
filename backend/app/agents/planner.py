"""
Planner Agent
Generates structured research outline from a topic
Pure function with no side effects
"""
import logging
from typing import List
from ..utils.openrouter import call_llm, OpenRouterError

logger = logging.getLogger(__name__)


async def plan_research(topic: str, max_sections: int = 5) -> List[str]:
    """
    Generate ordered list of research section titles from a topic
    
    Args:
        topic: Research topic (e.g., "Artificial Intelligence")
        max_sections: Maximum number of sections to generate (default 5)
    
    Returns:
        List[str]: Ordered list of section titles
    
    Raises:
        OpenRouterError: If LLM call fails
    
    Example:
        >>> sections = await plan_research("Machine Learning")
        >>> sections
        ['Introduction to Machine Learning', 'Key Concepts', 'Applications', ...]
    """
    
    prompt = f"""Generate a structured research outline for: "{topic}"

Create exactly {max_sections} section titles that would form a comprehensive research paper.
Make titles academic, specific, and in logical order.

Return ONLY the section titles, one per line, numbered.
Format:
1. Title One
2. Title Two
3. Title Three
...

Topic: {topic}
Sections:"""
    
    try:
        logger.info(f"Planning research for topic: {topic}")
        response = await call_llm(
            prompt,
            model=None,  # Uses default PLANNER_MODEL
            temperature=0.4,
            max_tokens=300
        )
        
        # Parse response to extract section titles
        sections = _parse_section_titles(response)
        
        if not sections:
            logger.warning(f"No sections extracted from planner response")
            # Fallback: return basic structure
            sections = _get_fallback_sections(topic)
        
        logger.info(f"Generated {len(sections)} sections for topic: {topic}")
        return sections
        
    except OpenRouterError as e:
        logger.error(f"Planner agent failed: {e}")
        raise


def _parse_section_titles(response: str) -> List[str]:
    """
    Extract section titles from LLM response
    Handles numbered lists and various formats
    
    Args:
        response: Raw LLM response text
    
    Returns:
        List[str]: Cleaned section titles
    """
    lines = response.strip().split('\n')
    sections = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Remove numbering (1., 1), etc.)
        if line and line[0].isdigit():
            # Find where the title starts (after number and punctuation)
            for i, char in enumerate(line):
                if not char.isdigit() and char not in '.):- ':
                    title = line[i:].strip()
                    if title:
                        sections.append(title)
                    break
        elif line and not line[0].isdigit():
            # Line doesn't start with number, might be a title
            sections.append(line)
    
    return sections[:5]  # Return max 5 sections


def _get_fallback_sections(topic: str) -> List[str]:
    """
    Provide fallback section structure when parsing fails
    
    Args:
        topic: Research topic
    
    Returns:
        List[str]: Default section structure
    """
    return [
        f"Introduction to {topic}",
        f"Key Concepts and Definitions",
        f"Historical Background and Development",
        f"Current Applications and Research",
        f"Future Perspectives and Conclusions"
    ]
