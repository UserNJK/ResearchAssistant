"""
Insight Agent
Extracts trends, gaps, and conclusions from summarized content
Pure function for analytical tasks
"""
import logging
from typing import List, Dict, Any
from ..utils.openrouter import call_llm, OpenRouterError

logger = logging.getLogger(__name__)


async def extract_insights(
    summaries: Dict[str, str],
    topic: str
) -> Dict[str, Any]:
    """
    Extract key insights, trends, and gaps from section summaries
    
    Args:
        summaries: Dictionary mapping section titles to summaries
        topic: Main research topic
    
    Returns:
        dict: Contains trends (list), gaps (list), conclusions (list)
    
    Raises:
        OpenRouterError: If LLM call fails
    
    Example:
        >>> insights = await extract_insights(summaries, "AI")
        >>> "trends" in insights and "gaps" in insights
        True
    """
    
    # Combine summaries for analysis
    combined_content = "\n\n".join([
        f"## {title}\n{summary}"
        for title, summary in summaries.items()
    ])
    
    prompt = f"""Analyze the following research summaries on "{topic}" and extract key insights.

Identify:
1. Current trends and patterns (3-4 items)
2. Research gaps or unexplored areas (2-3 items)
3. Main conclusions or findings (2-3 items)

Be specific and grounded in the content provided.

Content:
{combined_content}

Analysis Format:
TRENDS:
- Trend 1
- Trend 2

GAPS:
- Gap 1
- Gap 2

CONCLUSIONS:
- Conclusion 1
- Conclusion 2"""
    
    try:
        logger.info(f"Extracting insights from {len(summaries)} sections")
        response = await call_llm(
            prompt,
            model=None,  # Uses default INSIGHT_MODEL
            temperature=0.4,
            max_tokens=500
        )
        
        # Parse response into structured insights
        insights = _parse_insights_response(response)
        
        logger.info(f"Extracted insights: {len(insights['trends'])} trends, "
                   f"{len(insights['gaps'])} gaps, {len(insights['conclusions'])} conclusions")
        
        return insights
        
    except OpenRouterError as e:
        logger.error(f"Insight agent failed: {e}")
        raise


def _parse_insights_response(response: str) -> Dict[str, List[str]]:
    """
    Parse structured insight response from LLM
    
    Args:
        response: LLM response text
    
    Returns:
        dict: Parsed insights with trends, gaps, conclusions lists
    """
    sections = {
        "trends": [],
        "gaps": [],
        "conclusions": []
    }
    
    current_section = None
    
    for line in response.split('\n'):
        line = line.strip()
        
        if not line:
            continue
        
        # Detect section headers
        if "TRENDS:" in line.upper():
            current_section = "trends"
        elif "GAPS:" in line.upper():
            current_section = "gaps"
        elif "CONCLUSIONS:" in line.upper():
            current_section = "conclusions"
        
        # Extract bullet points
        elif line.startswith('-') and current_section:
            item = line.lstrip('-').strip()
            if item:
                sections[current_section].append(item)
        
        elif line.startswith('•') and current_section:
            item = line.lstrip('•').strip()
            if item:
                sections[current_section].append(item)
    
    # Ensure all sections have at least one item
    if not sections["trends"]:
        sections["trends"] = ["Key developments in the field"]
    if not sections["gaps"]:
        sections["gaps"] = ["Areas requiring further research"]
    if not sections["conclusions"]:
        sections["conclusions"] = ["Synthesis of findings from research"]
    
    return sections


async def identify_key_concepts(
    summaries: Dict[str, str],
    topic: str,
    max_concepts: int = 10
) -> List[str]:
    """
    Identify key concepts and terminology from summaries
    Helper function for reference indexing
    
    Args:
        summaries: Section summaries
        topic: Main research topic
        max_concepts: Maximum concepts to extract
    
    Returns:
        List[str]: Key concepts and terminology
    
    Raises:
        OpenRouterError: If LLM call fails
    """
    
    combined = "\n".join(summaries.values())
    
    prompt = f"""Identify the {max_concepts} most important key concepts and terms 
related to "{topic}" from the following research summaries.

List only the concepts/terms, one per line, without numbering or bullets.

Summaries:
{combined}

Key Concepts:"""
    
    try:
        logger.info(f"Identifying key concepts for {topic}")
        response = await call_llm(
            prompt,
            model=None,
            temperature=0.3,
            max_tokens=150
        )
        
        # Parse concepts (one per line)
        concepts = [
            line.strip()
            for line in response.split('\n')
            if line.strip() and len(line.strip()) > 2
        ][:max_concepts]
        
        logger.info(f"Identified {len(concepts)} key concepts")
        return concepts
        
    except OpenRouterError as e:
        logger.error(f"Concept extraction failed: {e}")
        return []
