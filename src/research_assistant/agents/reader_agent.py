"""Paper reading and analysis agent."""

import logging
import requests
from typing import Optional, Dict, Any
from pathlib import Path
from pypdf import PdfReader
from io import BytesIO
from bs4 import BeautifulSoup
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class PaperContent:
    """Represents extracted paper content."""
    url: str
    title: str
    text: str
    abstract: Optional[str] = None
    num_pages: Optional[int] = None
    success: bool = True
    error: Optional[str] = None


class PaperReadingAgent:
    """Agent for reading and extracting content from papers."""
    
    def __init__(self, timeout: int = 30):
        """Initialize the paper reading agent.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def read_paper(self, url: str) -> PaperContent:
        """Read and extract content from a paper.
        
        Args:
            url: URL of the paper
            
        Returns:
            PaperContent with extracted text
        """
        logger.info(f"Reading paper from: {url}")
        
        try:
            # Check if it's a PDF URL
            if url.endswith('.pdf') or 'pdf' in url.lower():
                return self._read_pdf(url)
            else:
                return self._read_webpage(url)
                
        except Exception as e:
            logger.error(f"Error reading paper from {url}: {e}")
            return PaperContent(
                url=url,
                title="",
                text="",
                success=False,
                error=str(e)
            )
    
    def _read_pdf(self, url: str) -> PaperContent:
        """Read PDF content.
        
        Args:
            url: PDF URL
            
        Returns:
            Extracted content
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            pdf_file = BytesIO(response.content)
            pdf_reader = PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            # Try to extract title from first page
            title = ""
            if pdf_reader.pages:
                first_page = pdf_reader.pages[0].extract_text()
                lines = first_page.split('\n')
                # Usually title is in first few lines
                title = lines[0] if lines else "Unknown Title"
            
            # Try to extract abstract (usually appears early in paper)
            abstract = self._extract_abstract(text)
            
            return PaperContent(
                url=url,
                title=title,
                text=text[:50000],  # Limit to first 50k chars
                abstract=abstract,
                num_pages=len(pdf_reader.pages),
                success=True
            )
            
        except Exception as e:
            logger.error(f"Error reading PDF: {e}")
            return PaperContent(
                url=url,
                title="",
                text="",
                success=False,
                error=str(e)
            )
    
    def _read_webpage(self, url: str) -> PaperContent:
        """Read content from a webpage.
        
        Args:
            url: Webpage URL
            
        Returns:
            Extracted content
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.find('title')
            title = title.get_text() if title else "Unknown Title"
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Try to extract abstract
            abstract = self._extract_abstract(text)
            
            return PaperContent(
                url=url,
                title=title,
                text=text[:50000],  # Limit to first 50k chars
                abstract=abstract,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Error reading webpage: {e}")
            return PaperContent(
                url=url,
                title="",
                text="",
                success=False,
                error=str(e)
            )
    
    def _extract_abstract(self, text: str) -> Optional[str]:
        """Extract abstract from paper text.
        
        Args:
            text: Full paper text
            
        Returns:
            Abstract text if found
        """
        text_lower = text.lower()
        
        # Look for abstract section
        abstract_markers = ['abstract', 'summary']
        
        for marker in abstract_markers:
            start = text_lower.find(marker)
            if start != -1:
                # Extract next 1000 characters after "abstract"
                start = start + len(marker)
                end = start + 1000
                abstract = text[start:end].strip()
                
                # Try to find where abstract ends (introduction, keywords, etc.)
                end_markers = ['introduction', '1.', 'keywords', 'key words']
                for end_marker in end_markers:
                    end_pos = abstract.lower().find(end_marker)
                    if end_pos != -1:
                        abstract = abstract[:end_pos].strip()
                        break
                
                return abstract if len(abstract) > 50 else None
        
        return None
