"""Main research workflow orchestrating all agents."""

import logging
from typing import TypedDict, Annotated, List, Dict, Any
from pathlib import Path
from datetime import datetime
import operator

from langgraph.graph import StateGraph, END

from .agents.search_agent import WebSearchAgent, SearchResult
from .agents.reader_agent import PaperReadingAgent, PaperContent
from .agents.writer_agent import ReportWritingAgent, ResearchReport
from .config import Config
from .utils.helpers import ensure_directory, sanitize_filename


logger = logging.getLogger(__name__)


class ResearchState(TypedDict):
    """State for the research workflow."""
    topic: str
    search_results: List[Dict[str, Any]]
    paper_contents: List[Dict[str, Any]]
    report: Dict[str, Any]
    error: str
    step: str


class ResearchWorkflow:
    """Orchestrates the research assistant workflow."""
    
    def __init__(self, config: Config):
        """Initialize the research workflow.
        
        Args:
            config: Configuration object
        """
        self.config = config
        
        # Initialize agents
        self.search_agent = WebSearchAgent(max_results=config.max_search_results)
        self.reader_agent = PaperReadingAgent()
        self.writer_agent = ReportWritingAgent(
            model_name=config.model_name,
            temperature=config.temperature,
            api_key=config.openai_api_key
        )
        
        # Create output directory
        ensure_directory(config.output_dir)
        
        # Build workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow.
        
        Returns:
            Compiled workflow graph
        """
        # Define the graph
        workflow = StateGraph(ResearchState)
        
        # Add nodes
        workflow.add_node("search", self._search_node)
        workflow.add_node("read_papers", self._read_papers_node)
        workflow.add_node("write_report", self._write_report_node)
        
        # Add edges
        workflow.set_entry_point("search")
        workflow.add_edge("search", "read_papers")
        workflow.add_edge("read_papers", "write_report")
        workflow.add_edge("write_report", END)
        
        return workflow.compile()
    
    def _search_node(self, state: ResearchState) -> ResearchState:
        """Search for papers and articles.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        logger.info(f"Searching for: {state['topic']}")
        
        try:
            # Search for papers
            results = self.search_agent.search_papers(state['topic'])
            
            # Convert to dict for state
            search_results = [
                {
                    'title': r.title,
                    'url': r.url,
                    'snippet': r.snippet,
                    'source': r.source
                }
                for r in results
            ]
            
            state['search_results'] = search_results
            state['step'] = 'search_completed'
            logger.info(f"Found {len(search_results)} results")
            
        except Exception as e:
            logger.error(f"Error in search node: {e}")
            state['error'] = str(e)
        
        return state
    
    def _read_papers_node(self, state: ResearchState) -> ResearchState:
        """Read and extract content from papers.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        logger.info("Reading papers...")
        
        paper_contents = []
        
        # Read top N papers
        urls_to_read = [
            r['url'] for r in state['search_results'][:self.config.max_papers_to_analyze]
        ]
        
        for url in urls_to_read:
            try:
                content = self.reader_agent.read_paper(url)
                
                if content.success:
                    paper_contents.append({
                        'url': content.url,
                        'title': content.title,
                        'text': content.text,
                        'abstract': content.abstract,
                        'num_pages': content.num_pages
                    })
                    logger.info(f"Successfully read: {content.title[:50]}")
                else:
                    logger.warning(f"Failed to read: {url}")
                    
            except Exception as e:
                logger.error(f"Error reading {url}: {e}")
        
        state['paper_contents'] = paper_contents
        state['step'] = 'reading_completed'
        logger.info(f"Successfully read {len(paper_contents)} papers")
        
        return state
    
    def _write_report_node(self, state: ResearchState) -> ResearchState:
        """Write the research report.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        logger.info("Writing report...")
        
        try:
            report = self.writer_agent.write_report(
                topic=state['topic'],
                search_results=state['search_results'],
                paper_contents=state['paper_contents']
            )
            
            state['report'] = {
                'topic': report.topic,
                'summary': report.summary,
                'detailed_analysis': report.detailed_analysis,
                'key_findings': report.key_findings,
                'references': report.references,
                'full_text': report.full_text
            }
            
            state['step'] = 'report_completed'
            logger.info("Report completed")
            
        except Exception as e:
            logger.error(f"Error writing report: {e}")
            state['error'] = str(e)
        
        return state
    
    def run(self, topic: str) -> ResearchReport:
        """Run the research workflow.
        
        Args:
            topic: Research topic
            
        Returns:
            Research report
        """
        logger.info(f"Starting research on: {topic}")
        
        # Initialize state
        initial_state: ResearchState = {
            'topic': topic,
            'search_results': [],
            'paper_contents': [],
            'report': {},
            'error': '',
            'step': 'initialized'
        }
        
        # Run workflow
        final_state = self.workflow.invoke(initial_state)
        
        # Save report to file
        if final_state.get('report'):
            self._save_report(final_state['report'])
        
        # Convert back to ResearchReport object
        report_data = final_state['report']
        return ResearchReport(
            topic=report_data['topic'],
            summary=report_data['summary'],
            detailed_analysis=report_data['detailed_analysis'],
            key_findings=report_data['key_findings'],
            references=report_data['references'],
            full_text=report_data['full_text']
        )
    
    def _save_report(self, report_data: Dict[str, Any]) -> Path:
        """Save report to file.
        
        Args:
            report_data: Report data dictionary
            
        Returns:
            Path to saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        topic_safe = sanitize_filename(report_data['topic'])
        filename = f"research_report_{topic_safe}_{timestamp}.md"
        filepath = self.config.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_data['full_text'])
        
        logger.info(f"Report saved to: {filepath}")
        return filepath
