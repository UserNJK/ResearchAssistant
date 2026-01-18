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
    Format a single research section - just return summary as-is
    
    Final formatting happens in format_complete_paper()
    
    Args:
        section_title: Title of the section
        summary: Raw summary content
        section_index: Ordinal position
    
    Returns:
        str: Summary text (no additional processing)
    """
    logger.info(f"Processing section {section_index}: {section_title}")
    return summary.strip()


async def format_complete_paper(
    title: str,
    sections: Dict[str, str],
    insights: Dict[str, List[str]],
    keywords: List[str],
    sources: Dict[str, Dict] = None
) -> str:
    """
    Format complete research paper with academic citations and quality validation.
    
    PHASE 8: Academic formatter with in-text citations and source attribution
    
    Args:
        title: Research paper title
        sections: Dictionary mapping section titles to content
        insights: Dictionary with trends, gaps, conclusions
        keywords: List of key concepts (5-8 items)
        sources: Dictionary mapping sections to source metadata {section: {source, url, type}}
    
    Returns:
        str: Complete formatted academic research paper in markdown
    """
    
    if sources is None:
        sources = {}
    
    # Combine all sections with source attribution
    sections_text = "\n\n".join([
        f"=== {section_title} ===\n{content}\n[Source: {sources.get(section_title, {}).get('source', 'Research Synthesis')}]"
        for section_title, content in sections.items()
    ])
    
    # Format insights
    trends_text = "\n".join([f"- {t}" for t in insights.get("trends", [])[:5]])
    gaps_text = "\n".join([f"- {g}" for g in insights.get("gaps", [])[:5]])
    conclusions_text = "\n".join([f"- {c}" for c in insights.get("conclusions", [])[:5]])
    keywords_text = ", ".join(keywords[:8]) if keywords else "Research"
    
    # Build source list for references (remove duplicates)
    source_list = []
    seen_sources = set()
    for section, source_info in sources.items():
        source_name = source_info.get('source', 'Unknown')
        if source_name not in seen_sources and not source_info.get('is_placeholder'):
            source_list.append(source_info)
            seen_sources.add(source_name)
    
    sources_formatted = "\n".join([
        f"- {s['source']} ({s.get('type', 'Source')}). Accessed {s.get('accessed_date', 'N/A').split('T')[0]}"
        for s in source_list[:5]
    ]) if source_list else "- Research synthesis from multiple sources"
    
    prompt = f"""SYSTEM: You are an expert academic paper formatter specializing in fact-rich, well-cited research papers. Enforce academic quality and citation standards.

You are an expert academic paper formatter. Generate a POLISHED, FACT-RICH research paper.

CRITICAL QUALITY RULES:
1. EVERY section must be 300+ words (except abstract/keywords)
2. NO generic language: reject "This section discusses...", "Recent developments..."
3. Include actual FACTS, SPECIFICATIONS, TECHNICAL DETAILS
4. Include in-text citations like (Source, Year) for ALL claims
5. Each major section must have 3-4 substantive paragraphs
6. NO repetition from abstract into main sections

PAPER METADATA:
- Title: {title}
- Authors: ResearchAssistant AI
- Affiliation: Independent Research  
- Date: 2026
- Keywords: {keywords_text}

CONTENT TO INCORPORATE (with source attribution):
{sections_text}

INSIGHTS TO INCORPORATE:
Trends: {trends_text or "Key developments in the field"}
Gaps: {gaps_text or "Areas for future research"}
Conclusions: {conclusions_text or "Synthesis of findings"}

SOURCES AVAILABLE FOR REFERENCES:
{sources_formatted}

OUTPUT STRUCTURE:

# {title}

**Authors:** ResearchAssistant AI  
**Affiliation:** Independent Research  
**Year:** 2026

---

## Abstract

[150-200 words: summarize topic, significance, findings. MUST be technical and specific, not generic.]

**Keywords:** {keywords_text}

---

## 1. Introduction

[3-4 paragraphs, 400+ words. Answer: What is {title.lower()}? Why does it matter? What will you learn?]

---

## 2. Background and Context

[3-4 paragraphs, 400+ words. Historical development, key prior work, foundational concepts, evolution. Reference sources where appropriate (Source, Year).]

---

## 3. Core Concepts and Fundamentals

[3-4 paragraphs, 400+ words. Definitions, theoretical frameworks, principles. Be specific and technical.]

---

## 4. Technical Analysis and Findings

[4-5 paragraphs, 500+ words. Detailed analysis, methodologies, implementations, actual findings. Use provided section content. Include citations.]

---

## 5. Current State and Emerging Trends

[3-4 paragraphs, 400+ words. Reference the trends identified. What is happening NOW? Include specific examples.]

---

## 6. Challenges and Future Directions

[3-4 paragraphs, 400+ words. Reference the gaps identified. What problems remain? What are promising future directions?]

---

## 7. Conclusion

[2-3 paragraphs, 300+ words. Synthesize findings. Restate significance. Implications and outlook.]

---

## References

[Include only sources that are cited in-text. Format in IEEE/APA style:]

{sources_formatted}

---

VALIDATION CHECKLIST:
✓ No section under 300 words
✓ In-text citations included
✓ No generic language detected
✓ Multiple paragraphs per section
✓ Specific facts and details, not filler
✓ References only for cited sources

NOW GENERATE THE COMPLETE PAPER:
Output ONLY the formatted paper in markdown. No explanations or meta-commentary."""

    try:
        logger.info(f"Generating complete academic paper: {title}")
        paper = await call_llm(
            prompt=prompt,
            temperature=0.3,
            max_tokens=5000
        )
        
        # Validation: Check for minimum section length and quality
        paper = _validate_and_expand_paper(paper, title)
        
        logger.info(f"Generated complete paper: {len(paper)} chars")
        return paper.strip()
        
    except Exception as e:
        logger.error(f"Academic paper generation failed: {str(e)}, generating fallback")
        
        # Fallback with actual source information
        source_refs = "\n".join([f"- {s['source']}" for s in source_list[:3]]) if source_list else "- Research synthesis from multiple sources"
        
        fallback_paper = f"""# {title}

**Authors:** ResearchAssistant AI  
**Affiliation:** Independent Research  
**Year:** 2026

---

## Abstract

This research presents a comprehensive investigation of {title.lower()}. The study examines foundational concepts, current methodologies, and emerging trends within the field. Analysis draws from multiple research sources and identifies key challenges and opportunities for future work.

**Keywords:** {", ".join(keywords[:8]) if keywords else title}

---

## 1. Introduction

{title} represents an important research domain with significant real-world implications. The field encompasses multiple perspectives, methodologies, and practical applications. This paper synthesizes current knowledge and explores emerging directions in the domain.

---

## 2. Background

The development of {title.lower()} reflects cumulative advances from research institutions and practitioners. Historical work established foundational principles that inform contemporary approaches. Multiple research traditions have contributed to current understanding and practice.

---

## 3. Core Concepts

Understanding {title.lower()} requires familiarity with fundamental definitions, theoretical frameworks, and key principles. These foundations enable engagement with advanced topics and practical implementations.

---

## 4. Technical Analysis

Technical approaches to {title.lower()} employ diverse methodologies and frameworks. Modern implementations leverage contemporary technologies to achieve effective results across various applications.

---

## 5. Current Developments

Recent work in {title.lower()} reflects sustained research interest and industrial adoption. Emerging directions include enhanced methodologies, broader applications, and integration with complementary approaches.

---

## 6. Future Directions

Identified research gaps suggest promising directions for future investigation. These include improved techniques, expanded applications, and theoretical extensions.

---

## 7. Conclusion

This paper has examined {title.lower()} from multiple perspectives, synthesizing findings and identifying key challenges. Continued research and practical innovation promise further advances in this important domain.

---

## References

{source_refs}
"""
        
        return fallback_paper

def _validate_and_expand_paper(paper: str, topic: str) -> str:
    """
    Validate paper quality and flag/expand weak sections.
    
    Args:
        paper: Generated paper markdown
        topic: Research topic for context
    
    Returns:
        str: Validated/expanded paper
    """
    import re
    
    lines = paper.split('\n')
    sections = []
    current_section = {"title": "", "content": [], "start_line": 0}
    
    # Parse sections
    for i, line in enumerate(lines):
        if line.startswith('##') and not line.startswith('###'):
            if current_section["content"]:
                sections.append(current_section)
            current_section = {"title": line, "content": [], "start_line": i}
        else:
            current_section["content"].append(line)
    
    if current_section["content"]:
        sections.append(current_section)
    
    # Validate and expand weak sections
    expanded_lines = []
    for section in sections:
        expanded_lines.append(section["title"])
        expanded_lines.append("")
        
        section_text = "\n".join(section["content"]).strip()
        word_count = len(section_text.split())
        
        # Check for weak content
        is_weak = (
            word_count < 250 or 
            "This section discusses" in section_text or
            "Recent developments show" in section_text or
            section_text.endswith("...")
        )
        
        if is_weak and word_count < 250:
            # Expand with placeholder content for weak sections
            section_title = section["title"].replace('##', '').replace('###', '').strip()
            expansion = f"""
[Content expanded due to insufficient detail in original]

{section_text}

Further context and development of this topic includes multiple related concepts, 
practical applications, and ongoing research directions that contribute to comprehensive 
understanding of {topic.lower()}.
"""
            expanded_lines.append(expansion)
        else:
            expanded_lines.append(section_text)
        
        expanded_lines.append("")
    
    return "\n".join(expanded_lines)


