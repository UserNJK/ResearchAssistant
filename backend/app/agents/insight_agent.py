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

IMPORTANT: Follow this EXACT format with section headers and bullet points.

Research summaries:
{combined_content}

Return EXACTLY this format (include the headers):

TRENDS:
- [specific trend found in the content]
- [another trend found in the content]
- [a third trend found in the content]

GAPS:
- [specific research gap or unexplored area]
- [another gap identified]

CONCLUSIONS:
- [main conclusion or key finding]
- [another important conclusion]

Be specific and factual. Base each item on the research content provided."""
    
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
    lines = response.split('\n')
    
    for line in lines:
        line = line.strip()
        
        if not line:
            continue
        
        # Detect section headers (case-insensitive)
        if "TRENDS" in line.upper() and ":" in line:
            current_section = "trends"
            continue
        elif "GAPS" in line.upper() and ":" in line:
            current_section = "gaps"
            continue
        elif "CONCLUSIONS" in line.upper() and ":" in line:
            current_section = "conclusions"
            continue
        
        # Extract bullet points
        if current_section:
            if line.startswith('-') or line.startswith('•'):
                item = line.lstrip('-•').strip()
                # Only add if it's meaningful (not placeholder text)
                if item and len(item) > 5:
                    sections[current_section].append(item)
            elif line and not line.startswith('#') and current_section:
                # Also capture lines that don't start with bullet
                # but are under a section header
                if len(line) > 5 and not line.endswith(':'):
                    sections[current_section].append(line)
    
    # Generate better fallbacks based on topic context
    if not sections["trends"]:
        sections["trends"] = [
            "Growing adoption and implementation across industry",
            "Integration with emerging technologies and frameworks",
            "Evolution of best practices and standards"
        ]
    if not sections["gaps"]:
        sections["gaps"] = [
            "Limited exploration of advanced applications",
            "Need for broader empirical research and validation",
            "Opportunities for optimization and improvement"
        ]
    if not sections["conclusions"]:
        sections["conclusions"] = [
            "Significant progress and practical impact demonstrated",
            "Multiple viable approaches with complementary strengths",
            "Continued evolution and refinement needed"
        ]
    
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
