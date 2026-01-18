"""Report writing agent using LangChain."""

import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain


logger = logging.getLogger(__name__)


@dataclass
class ResearchReport:
    """Represents a research report."""
    topic: str
    summary: str
    detailed_analysis: str
    key_findings: List[str]
    references: List[str]
    full_text: str


class ReportWritingAgent:
    """Agent for writing research reports using LLM."""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7, api_key: Optional[str] = None):
        """Initialize the report writing agent.
        
        Args:
            model_name: Name of the LLM model to use
            temperature: Temperature for generation
            api_key: OpenAI API key (optional)
        """
        self.model_name = model_name
        self.temperature = temperature
        self.api_key = api_key
        
        # Initialize LLM only if API key is provided
        self.llm = None
        if api_key:
            try:
                self.llm = ChatOpenAI(
                    model_name=model_name,
                    temperature=temperature,
                    openai_api_key=api_key
                )
            except Exception as e:
                logger.warning(f"Could not initialize LLM: {e}")
    
    def write_report(
        self,
        topic: str,
        search_results: List[Dict[str, Any]],
        paper_contents: List[Dict[str, Any]]
    ) -> ResearchReport:
        """Write a comprehensive research report.
        
        Args:
            topic: Research topic
            search_results: List of search results
            paper_contents: List of paper contents
            
        Returns:
            Generated research report
        """
        logger.info(f"Writing report on: {topic}")
        
        # If no LLM available, create a basic report
        if not self.llm:
            return self._create_basic_report(topic, search_results, paper_contents)
        
        try:
            # Create report using LLM
            return self._create_llm_report(topic, search_results, paper_contents)
        except Exception as e:
            logger.error(f"Error creating LLM report: {e}")
            return self._create_basic_report(topic, search_results, paper_contents)
    
    def _create_llm_report(
        self,
        topic: str,
        search_results: List[Dict[str, Any]],
        paper_contents: List[Dict[str, Any]]
    ) -> ResearchReport:
        """Create report using LLM.
        
        Args:
            topic: Research topic
            search_results: List of search results
            paper_contents: List of paper contents
            
        Returns:
            Generated research report
        """
        # Prepare context from papers
        context = self._prepare_context(search_results, paper_contents)
        
        # Create summary
        summary_prompt = PromptTemplate(
            input_variables=["topic", "context"],
            template="""You are a research assistant. Write a concise summary (2-3 paragraphs) about {topic} based on the following research materials:

{context}

Summary:"""
        )
        
        summary_chain = LLMChain(llm=self.llm, prompt=summary_prompt)
        summary = summary_chain.run(topic=topic, context=context[:8000])
        
        # Create detailed analysis
        analysis_prompt = PromptTemplate(
            input_variables=["topic", "context"],
            template="""You are a research assistant. Write a detailed analysis of {topic} based on the following research materials:

{context}

Include:
1. Background and context
2. Current state of research
3. Key methodologies
4. Main findings and results
5. Future directions

Detailed Analysis:"""
        )
        
        analysis_chain = LLMChain(llm=self.llm, prompt=analysis_prompt)
        detailed_analysis = analysis_chain.run(topic=topic, context=context[:8000])
        
        # Extract key findings
        findings_prompt = PromptTemplate(
            input_variables=["topic", "context"],
            template="""Based on the research about {topic}, list 5-7 key findings:

{context}

Key Findings (one per line, starting with -):"""
        )
        
        findings_chain = LLMChain(llm=self.llm, prompt=findings_prompt)
        findings_text = findings_chain.run(topic=topic, context=context[:8000])
        key_findings = [line.strip('- ').strip() for line in findings_text.split('\n') if line.strip().startswith('-')]
        
        # Collect references
        references = [result.get('url', '') for result in search_results if result.get('url')]
        
        # Create full report text
        full_text = self._format_full_report(topic, summary, detailed_analysis, key_findings, references)
        
        return ResearchReport(
            topic=topic,
            summary=summary,
            detailed_analysis=detailed_analysis,
            key_findings=key_findings,
            references=references,
            full_text=full_text
        )
    
    def _create_basic_report(
        self,
        topic: str,
        search_results: List[Dict[str, Any]],
        paper_contents: List[Dict[str, Any]]
    ) -> ResearchReport:
        """Create a basic report without LLM.
        
        Args:
            topic: Research topic
            search_results: List of search results
            paper_contents: List of paper contents
            
        Returns:
            Generated research report
        """
        # Create summary from search snippets
        summary_parts = []
        for i, result in enumerate(search_results[:5], 1):
            snippet = result.get('snippet', '')
            if snippet:
                summary_parts.append(f"{i}. {snippet}")
        
        summary = f"Research on {topic}:\n\n" + "\n\n".join(summary_parts)
        
        # Create detailed analysis from paper contents
        analysis_parts = []
        for i, paper in enumerate(paper_contents, 1):
            title = paper.get('title', 'Unknown')
            abstract = paper.get('abstract', '')
            text_preview = paper.get('text', '')[:500]
            
            analysis_parts.append(f"## Paper {i}: {title}\n\n")
            if abstract:
                analysis_parts.append(f"Abstract: {abstract}\n\n")
            else:
                analysis_parts.append(f"Preview: {text_preview}...\n\n")
        
        detailed_analysis = "\n".join(analysis_parts)
        
        # Extract key findings from titles and snippets
        key_findings = []
        for result in search_results[:7]:
            title = result.get('title', '')
            if title:
                key_findings.append(title)
        
        # Collect references
        references = [result.get('url', '') for result in search_results if result.get('url')]
        
        # Create full report
        full_text = self._format_full_report(topic, summary, detailed_analysis, key_findings, references)
        
        return ResearchReport(
            topic=topic,
            summary=summary,
            detailed_analysis=detailed_analysis,
            key_findings=key_findings,
            references=references,
            full_text=full_text
        )
    
    def _prepare_context(self, search_results: List[Dict[str, Any]], paper_contents: List[Dict[str, Any]]) -> str:
        """Prepare context for LLM from search results and papers.
        
        Args:
            search_results: List of search results
            paper_contents: List of paper contents
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        # Add search results
        context_parts.append("## Search Results:")
        for i, result in enumerate(search_results[:5], 1):
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            context_parts.append(f"{i}. {title}: {snippet}")
        
        # Add paper contents
        context_parts.append("\n## Research Papers:")
        for i, paper in enumerate(paper_contents[:3], 1):
            title = paper.get('title', '')
            abstract = paper.get('abstract', '')
            text = paper.get('text', '')[:2000]  # First 2000 chars
            
            context_parts.append(f"\n### Paper {i}: {title}")
            if abstract:
                context_parts.append(f"Abstract: {abstract}")
            else:
                context_parts.append(f"Content preview: {text}")
        
        return "\n".join(context_parts)
    
    def _format_full_report(
        self,
        topic: str,
        summary: str,
        detailed_analysis: str,
        key_findings: List[str],
        references: List[str]
    ) -> str:
        """Format the complete report as markdown.
        
        Args:
            topic: Research topic
            summary: Summary text
            detailed_analysis: Detailed analysis
            key_findings: List of key findings
            references: List of reference URLs
            
        Returns:
            Formatted markdown report
        """
        report_parts = [
            f"# Research Report: {topic}\n",
            f"## Executive Summary\n",
            summary,
            "\n## Key Findings\n",
        ]
        
        for finding in key_findings:
            report_parts.append(f"- {finding}")
        
        report_parts.extend([
            "\n## Detailed Analysis\n",
            detailed_analysis,
            "\n## References\n",
        ])
        
        for i, ref in enumerate(references, 1):
            report_parts.append(f"{i}. {ref}")
        
        return "\n".join(report_parts)
