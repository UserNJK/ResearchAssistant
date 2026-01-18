"""Web search agent using DuckDuckGo (free)."""

import logging
from typing import List, Dict, Any
from duckduckgo_search import DDGS
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Represents a search result."""
    title: str
    url: str
    snippet: str
    source: str = "duckduckgo"


class WebSearchAgent:
    """Agent for searching the web using free search APIs."""
    
    def __init__(self, max_results: int = 10):
        """Initialize the web search agent.
        
        Args:
            max_results: Maximum number of results to return
        """
        self.max_results = max_results
        self.ddgs = DDGS()
    
    def search(self, query: str) -> List[SearchResult]:
        """Search for papers and articles.
        
        Args:
            query: Search query
            
        Returns:
            List of search results
        """
        logger.info(f"Searching for: {query}")
        results = []
        
        try:
            # Use DuckDuckGo search (free and no API key needed)
            ddg_results = self.ddgs.text(
                query,
                max_results=self.max_results
            )
            
            for result in ddg_results:
                results.append(SearchResult(
                    title=result.get('title', ''),
                    url=result.get('href', ''),
                    snippet=result.get('body', ''),
                    source='duckduckgo'
                ))
            
            logger.info(f"Found {len(results)} results")
            
        except Exception as e:
            logger.error(f"Error during search: {e}")
        
        return results
    
    def search_papers(self, topic: str) -> List[SearchResult]:
        """Search specifically for research papers.
        
        Args:
            topic: Research topic
            
        Returns:
            List of paper search results
        """
        # Enhance query to find academic papers
        enhanced_query = f"{topic} site:arxiv.org OR site:scholar.google.com OR site:researchgate.net OR filetype:pdf"
        return self.search(enhanced_query)
    
    def search_general(self, query: str) -> List[SearchResult]:
        """General web search.
        
        Args:
            query: Search query
            
        Returns:
            List of search results
        """
        return self.search(query)
