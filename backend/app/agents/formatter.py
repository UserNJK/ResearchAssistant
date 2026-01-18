"""
Formatting Agent
Converts analyzed research into academic-style formatted output
Pure function for presentation layer
"""
import logging
from typing import List, Dict, Any
from ..utils.openrouter import call_llm, OpenRouterError

logger = logging.getLogger(__name__)


async def format_section(
    section_title: str,
    summary: str,
    section_index: int
) -> str:
    """
    Format a single research section with academic styling
    
    Args:
        section_title: Title of the section
        summary: Summarized content
        section_index: Ordinal position (1, 2, 3, ...)
    
    Returns:
        str: Formatted section with markdown styling
    
    Raises:
        OpenRouterError: If formatting LLM call fails
    
    Example:
        >>> formatted = await format_section("Introduction", content, 1)
        >>> "## " in formatted
        True
    """
    
    prompt = f"""Format the following research section with proper academic styling.

Make it:
- Clear and well-structured
- Academic in tone
- Properly formatted with paragraphs
- Logical and readable

Original section:
Title: {section_title}
Content: {summary}

Formatted output (use markdown, start with ## for the title):"""
    
    try:
        logger.info(f"Formatting section {section_index}: {section_title}")
        formatted = await call_llm(
            prompt,
            model=None,  # Uses default FORMATTER_MODEL
            temperature=0.3,  # Lower temp for consistency
            max_tokens=600
        )
        
        # Ensure proper markdown formatting
        if not formatted.startswith("##"):
            formatted = f"## {section_title}\n\n{formatted}"
        
        logger.info(f"Formatted section: {len(formatted)} chars")
        return formatted.strip()
        
    except OpenRouterError as e:
        logger.error(f"Formatting agent failed on {section_title}: {e}")
        raise


async def format_complete_paper(
    title: str,
    sections: Dict[str, str],
    insights: Dict[str, List[str]],
    keywords: List[str]
) -> str:
    """
    Format complete research paper with all sections and metadata
    
    Args:
        title: Research paper title (topic)
        sections: Dictionary mapping section titles to formatted content
        insights: Dictionary with trends, gaps, conclusions
        keywords: Key concepts and terminology
    
    Returns:
        str: Complete formatted research paper in markdown
    
    Note:
        This is a composition function - formats the entire paper structure.
    """
    
    paper = []
    
    # Title and metadata
    paper.append(f"# {title}")
    paper.append("")
    paper.append(f"**Keywords:** {', '.join(keywords[:8])}")
    paper.append("")
    
    # Abstract/Overview
    paper.append("## Overview")
    paper.append(
        f"This research paper provides a comprehensive analysis of {title}. "
        f"It explores key concepts, current trends, and identifies areas for future research."
    )
    paper.append("")
    
    # Main sections
    paper.append("## Research Content")
    paper.append("")
    for section_title, content in sections.items():
        paper.append(content)
        paper.append("")
    
    # Insights section
    paper.append("## Key Findings")
    paper.append("")
    
    if insights.get("trends"):
        paper.append("### Current Trends")
        for trend in insights["trends"]:
            paper.append(f"- {trend}")
        paper.append("")
    
    if insights.get("gaps"):
        paper.append("### Research Gaps")
        for gap in insights["gaps"]:
            paper.append(f"- {gap}")
        paper.append("")
    
    if insights.get("conclusions"):
        paper.append("### Conclusions")
        for conclusion in insights["conclusions"]:
            paper.append(f"- {conclusion}")
        paper.append("")
    
    # Metadata footer
    paper.append("---")
    paper.append("*This research paper was generated using multi-agent AI analysis.*")
    
    return "\n".join(paper)


async def add_citations_markup(content: str, topic: str) -> str:
    """
    Add citation placeholders and research context to content
    Helper function for academic formatting
    
    Args:
        content: Formatted content
        topic: Research topic for context
    
    Returns:
        str: Content with citation markup added
    
    Raises:
        OpenRouterError: If LLM call fails
    """
    
    prompt = f"""Review the following academic content about "{topic}" and identify 
where citations would be appropriate. Add [CITATION NEEDED] markers where citations 
should appear.

Keep the content unchanged otherwise - only add citation markers.

Content:
{content}

Content with citation markers:"""
    
    try:
        logger.info(f"Adding citation markers to content")
        result = await call_llm(
            prompt,
            model=None,
            temperature=0.2,  # Very consistent for structural changes
            max_tokens=len(content) // 4 + 100
        )
        
        logger.info(f"Added citations to content")
        return result.strip()
        
    except OpenRouterError as e:
        logger.error(f"Citation markup failed: {e}")
        # Return original if formatting fails
        return content
