"""
Search Agent
Fetches rich information for research sections using LLM knowledge first,
with Wikipedia metadata and structured placeholders as fallbacks.
"""
import logging
import httpx
from typing import List, Dict, Any
import asyncio
from ..utils.openrouter import call_llm, OpenRouterError

logger = logging.getLogger(__name__)


async def search_for_section(section_title: str, topic: str) -> Dict[str, Any]:
    """
    Fetch relevant information for a research section WITH source attribution.
    Prioritize LLM built-in knowledge (budget-friendly model) for richer content,
    fall back to Wikipedia with metadata, then structured placeholders.
    
    Args:
        section_title: Title of the research section
        topic: Main research topic
    
    Returns:
        dict: {"content": text, "source": metadata, "url": url}
    
    Example:
        >>> result = await search_for_section("Introduction", "Machine Learning")
        >>> result["content"] and result["source"]
        True
    """
    try:
        logger.info(f"LLM-first search: topic='{topic}' section='{section_title}'")

        # 1) Try LLM knowledge (uses settings.DEFAULT_FALLBACK_MODEL, e.g. Mistral 7B)
        llm_result = await _search_llm_with_knowledge(topic, section_title)
        if llm_result and llm_result.get("content") and len(llm_result["content"]) > 200:
            logger.info(f"LLM produced {len(llm_result['content'])} chars of content")
            return llm_result

        # 2) Fallback to Wikipedia with metadata
        logger.info("LLM content insufficient; falling back to Wikipedia")
        wiki_result = await _search_wikipedia_with_metadata(topic)
        if wiki_result and wiki_result.get("content") and len(wiki_result["content"]) > 100:
            logger.info(f"Wikipedia provided {len(wiki_result['content'])} chars")
            return wiki_result

        # 3) Structured placeholder WITH metadata
        logger.warning("Search produced limited content; using structured placeholder")
        return _create_placeholder_with_metadata(topic, section_title)

    except OpenRouterError as e:
        logger.error(f"LLM search error: {e}")
        return _create_placeholder_with_metadata(topic, section_title)
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return _create_placeholder_with_metadata(topic, section_title)

async def _search_llm_with_knowledge(topic: str, section_title: str) -> Dict[str, Any] | None:
    """
    Use a budget-friendly LLM via OpenRouter (default: Mistral 7B) to generate
    detailed, domain-specific content with built-in knowledge. Keeps temperature low
    for factual tone and limits tokens for cost control.
    """
    prompt = (
        "You are a domain expert research assistant. Write a detailed, factual "
        "section for an academic paper.\n\n"
        f"TOPIC: {topic}\n"
        f"SECTION: {section_title}\n\n"
        "Requirements:\n"
        "- 400-700 words with specific facts, concepts, and examples\n"
        "- Avoid generic phrases like 'This section discusses...'\n"
        "- Use precise, domain terminology\n"
        "- Organize into 2-4 substantive paragraphs\n"
        "- If known, mention widely recognized frameworks, methods, or standards\n"
        "- Do NOT invent references; this is source-neutral content\n"
        "Return only the section text."
    )

    try:
        content = await call_llm(
            prompt=prompt,
            # Use default configured model (budget-friendly): settings.DEFAULT_FALLBACK_MODEL
            model=None,
            temperature=0.3,
            max_tokens=1100,
            use_cache=True,
        )

        if not content or len(content.strip()) < 200:
            return None

        return {
            "content": content.strip(),
            "source": f"LLM Knowledge Synthesis - {topic}",
            "url": "internal://llm-knowledge",
            "query": topic,
            "type": "llm-knowledge",
            "accessed_date": __import__("datetime").datetime.now().isoformat(),
            "is_placeholder": False,
        }
    except Exception as e:
        logger.error(f"LLM knowledge search failed: {e}")
        return None


async def _search_wikipedia_with_metadata(query: str) -> Dict[str, Any]:
    """
    Search Wikipedia and extract content WITH source metadata.
    
    Returns:
        dict: {"content": text, "source": "Wikipedia - Topic", "url": url, "query": query}
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            params = {
                "action": "query",
                "format": "json",
                "titles": query,
                "prop": "extracts|info",
                "explaintext": True,
                "exintro": False,
                "exlimit": 1
            }
            
            headers = {
                "User-Agent": "ResearchAssistant/1.0 (research.assistant@example.com)"
            }
            
            response = await client.get(
                "https://en.wikipedia.org/w/api.php",
                params=params,
                headers=headers
            )
            
            if response.status_code != 200:
                logger.warning(f"Wikipedia API returned {response.status_code}")
                return None
            
            data = response.json()
            pages = data.get("query", {}).get("pages", {})
            if not pages:
                logger.warning("No Wikipedia pages found")
                return None
            
            page = next(iter(pages.values()))
            content = page.get("extract", "")
            title = page.get("title", query)
            page_id = page.get("pageid")
            
            if not content:
                return None
            
            # Build source metadata
            wiki_url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
            source_citation = f"Wikipedia - {title}"
            
            return {
                "content": content[:2000],  # Limit to first 2000 chars
                "source": source_citation,
                "url": wiki_url,
                "query": query,
                "type": "encyclopedia",
                "accessed_date": __import__("datetime").datetime.now().isoformat()
            }
            
    except httpx.TimeoutException:
        logger.warning("Wikipedia search timed out")
        return None
    except Exception as e:
        logger.error(f"Wikipedia search error: {e}")
        return None


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
                params=params,
                headers={"User-Agent": "ResearchAssistant/1.0 (research.assistant@example.com)"}
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


def _create_placeholder_with_metadata(topic: str, section: str) -> Dict[str, Any]:
    """
    Create structured placeholder content WITH source metadata.
    
    Returns:
        dict: {"content": text, "source": metadata}
    """
    section_lower = section.lower()
    
    # Section-specific content templates
    if "introduction" in section_lower:
        content = f"""{topic} represents a significant and evolving area of research with 
practical implications across multiple domains. The importance of {topic.lower()} has grown 
substantially due to technological advances and increased recognition of its applicability. 
This section provides foundational context and motivation for studying {topic.lower()} 
in depth. Understanding the landscape requires familiarity with key concepts, historical 
development, and current trends that have shaped the field's evolution."""
    
    elif "background" in section_lower or "literature" in section_lower:
        content = f"""The historical development of {topic} spans decades of research, with 
pioneering work establishing key theoretical foundations. Early research identified core 
principles that continue to inform current practice. Subsequent developments have extended 
these foundations through both theoretical innovations and practical applications. The 
field has benefited from contributions from academic institutions, research organizations, 
and industry practitioners. Contemporary understanding reflects cumulative advances and 
refined methodologies that address limitations of earlier approaches."""
    
    elif "fundamental" in section_lower or "concept" in section_lower or "core" in section_lower:
        content = f"""Understanding {topic.lower()} requires familiarity with several key concepts 
and theoretical frameworks. Central concepts include the core principles that define the field, 
fundamental definitions that establish common terminology, and theoretical models that explain 
how systems and processes work. These foundations support more advanced topics and practical 
applications. Related concepts from adjacent fields often provide additional insights and 
methodologies. Mastery of these concepts is essential for productive engagement with technical 
literature and practical implementations in the domain."""
    
    elif "technical" in section_lower or "analysis" in section_lower:
        content = f"""Technical approaches to {topic.lower()} encompass diverse methodologies, 
algorithms, and implementation strategies. Different techniques involve distinct trade-offs 
between performance metrics including computational efficiency, accuracy, scalability, and 
resource requirements. Modern implementations leverage contemporary technologies including 
distributed computing, cloud infrastructure, and sophisticated software frameworks. 
Practical considerations include deployment strategies, maintenance requirements, and 
integration with existing systems. Evaluating technical approaches requires understanding 
both theoretical properties and empirical performance characteristics."""
    
    elif "trend" in section_lower or "current" in section_lower:
        content = f"""Recent developments in {topic.lower()} reflect growing research interest 
and industrial adoption. Emerging directions include enhanced scalability, improved efficiency, 
better integration with machine learning approaches, and cloud-based solutions. Standards 
development efforts have increased, promoting interoperability and best practices. Open-source 
communities contribute significantly to methodological advancement and tool development. 
Real-world applications continue to expand across industries. The convergence of multiple 
technology trends has created new opportunities and revealed new challenges that drive 
continued research and development activity."""
    
    else:
        content = f"""This section examines {topic.lower()} from multiple analytical perspectives. 
The material covers foundational principles, contemporary practices, and evolving methodologies. 
Key aspects include theoretical foundations, practical implementations, industry standards, 
research opportunities, and integration with complementary technologies. The field continues 
to mature with improved tools, enhanced standards, and better understanding of fundamental 
trade-offs and limitations. Sustained research effort across academia and industry continues 
to advance the state of knowledge and practice."""
    
    return {
        "content": content,
        "source": "Research Synthesis - Placeholder",
        "url": "internal://synthesis",
        "query": topic,
        "type": "synthesized",
        "accessed_date": __import__("datetime").datetime.now().isoformat(),
        "is_placeholder": True
    }


def _create_placeholder_content(topic: str, section: str) -> str:
    """
    Create structured placeholder content when search fails
    Section-specific content for better quality fallback
    
    Args:
        topic: Main research topic
        section: Section title
    
    Returns:
        str: Placeholder content
    """
    section_lower = section.lower()
    
    # Section-specific content templates
    if "introduction" in section_lower:
        content = f"""{topic} represents a significant and evolving area of research with 
practical implications across multiple domains. The importance of {topic.lower()} has grown 
substantially due to technological advances and increased recognition of its applicability. 
This section provides foundational context and motivation for studying {topic.lower()} 
in depth."""
    
    elif "background" in section_lower or "literature" in section_lower:
        content = f"""The historical development of {topic} spans decades of research, with 
pioneering work establishing key theoretical foundations. Early research identified core 
principles that continue to inform current practice. Subsequent developments have extended 
these foundations through both theoretical innovations and practical applications. The 
field has benefited from contributions from academic institutions, research organizations, 
and industry practitioners."""
    
    elif "fundamental" in section_lower or "concept" in section_lower or "core" in section_lower:
        content = f"""Understanding {topic.lower()} requires familiarity with several key concepts 
and theoretical frameworks. Central concepts include the core principles that define the field, 
fundamental definitions that establish common terminology, and theoretical models that explain 
how systems and processes work. These foundations support more advanced topics and practical 
applications. Related concepts from adjacent fields often provide additional insights and 
methodologies."""
    
    elif "technical" in section_lower or "analysis" in section_lower:
        content = f"""Technical approaches to {topic.lower()} encompass diverse methodologies, 
algorithms, and implementation strategies. Different techniques involve distinct trade-offs 
between performance metrics including computational efficiency, accuracy, scalability, and 
resource requirements. Modern implementations leverage contemporary technologies including 
distributed computing, cloud infrastructure, and sophisticated software frameworks. 
Practical considerations include deployment strategies, maintenance requirements, and 
integration with existing systems."""
    
    elif "trend" in section_lower or "current" in section_lower:
        content = f"""Recent developments in {topic.lower()} reflect growing research interest 
and industrial adoption. Emerging directions include enhanced scalability, improved efficiency, 
better integration with machine learning approaches, and cloud-based solutions. Standards 
development efforts have increased, promoting interoperability and best practices. Open-source 
communities contribute significantly to methodological advancement and tool development. 
Real-world applications continue to expand across industries."""
    
    else:
        content = f"""This section examines {topic.lower()} from multiple analytical perspectives. 
The material covers foundational principles, contemporary practices, and evolving methodologies. 
Key aspects include theoretical foundations, practical implementations, industry standards, 
research opportunities, and integration with complementary technologies. The field continues 
to mature with improved tools, enhanced standards, and better understanding of fundamental 
trade-offs and limitations."""
    
    return f"""
## {section}

{content}

### Key Points
- Core principles and fundamental concepts
- Historical development and evolution  
- Current methodologies and best practices
- Emerging trends and future directions
- Integration with related technologies

### Significance
Work in {topic.lower()} continues to advance through both theoretical research and practical 
application. Understanding multiple perspectives strengthens the ability to apply these 
concepts effectively in real-world contexts.
"""
