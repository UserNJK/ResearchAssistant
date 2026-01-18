"""Configuration management for Research Assistant."""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field


class Config(BaseModel):
    """Configuration settings for Research Assistant."""
    
    # API Keys (can use free alternatives)
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key (optional)")
    
    # Search settings
    max_search_results: int = Field(default=10, description="Maximum number of search results to retrieve")
    
    # Paper processing
    max_papers_to_analyze: int = Field(default=5, description="Maximum number of papers to analyze in detail")
    
    # Output settings
    output_dir: Path = Field(default=Path("research_output"), description="Directory for output files")
    
    # Model settings (using free/open models as default)
    model_name: str = Field(default="gpt-3.5-turbo", description="LLM model to use")
    temperature: float = Field(default=0.7, description="Temperature for LLM generation")
    
    class Config:
        arbitrary_types_allowed = True
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            max_search_results=int(os.getenv("MAX_SEARCH_RESULTS", "10")),
            max_papers_to_analyze=int(os.getenv("MAX_PAPERS_TO_ANALYZE", "5")),
            output_dir=Path(os.getenv("OUTPUT_DIR", "research_output")),
            model_name=os.getenv("MODEL_NAME", "gpt-3.5-turbo"),
            temperature=float(os.getenv("TEMPERATURE", "0.7"))
        )
