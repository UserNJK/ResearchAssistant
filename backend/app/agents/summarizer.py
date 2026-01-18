"""
Summarization Agent
Condenses raw content into concise, focused summaries
Pure function with deterministic output
"""
import logging
from typing import Optional
from ..utils.openrouter import call_llm, OpenRouterError

logger = logging.getLogger(__name__)


async def summarize_content(
    raw_content: str,
    section_title: str,
    max_length: int = 300
) -> str:
    """
    Summarize raw content into a concise academic summary
    
    Args:
        raw_content: Raw text content to summarize
        section_title: Title of the section (for context)
        max_length: Maximum length of summary in words (default 300)
    
    Returns:
        str: Concise summary of the content
    
    Raises:
        OpenRouterError: If LLM call fails
    
    Example:
        >>> summary = await summarize_content(long_text, "Introduction")
        >>> len(summary.split()) <= 300
        True
    """
    
    # Truncate input if too long (prevent excessive token usage)
    if len(raw_content) > 3000:
        raw_content = raw_content[:3000] + "..."
        logger.info("Content truncated to 3000 chars for summarization")
    
    prompt = f"""Summarize the following content for the section: "{section_title}"

Create a concise academic summary in approximately {max_length} words.
Focus on key concepts, important points, and relevant information.
Maintain academic tone and remove redundant information.

Content to summarize:
{raw_content}

Summary for "{section_title}":"""
    
    try:
        logger.info(f"Summarizing content for section: {section_title}")
        summary = await call_llm(
            prompt,
            model=None,  # Uses default SUMMARY_MODEL
            temperature=0.3,  # Lower temp for consistency
            max_tokens=400  # Typically ~300 words in tokens
        )
        
        # Validate summary
        if not summary or len(summary) < 20:
            logger.warning("Summary too short, returning original content trimmed")
            return raw_content[:500]
        
        logger.info(f"Generated summary: {len(summary)} chars")
        return summary.strip()
        
    except OpenRouterError as e:
        logger.error(f"Summarization agent failed: {e}")
        raise


async def batch_summarize(
    content_dict: dict,
    max_length: int = 300
) -> dict:
    """
    Summarize multiple sections sequentially
    
    Args:
        content_dict: Dictionary mapping section titles to content
        max_length: Maximum length per summary
    
    Returns:
        dict: Dictionary mapping section titles to summaries
    
    Note:
        This is a helper - agents themselves are pure functions.
        Used by orchestrator in PHASE 4.
    """
    summaries = {}
    
    for section_title, content in content_dict.items():
        try:
            summary = await summarize_content(content, section_title, max_length)
            summaries[section_title] = summary
        except OpenRouterError as e:
            logger.error(f"Failed to summarize {section_title}: {e}")
            summaries[section_title] = f"[Summary failed: {str(e)[:100]}]"
    
    return summaries
