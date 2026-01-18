"""
Example usage of the Research Assistant.

This script demonstrates how to use the Research Assistant programmatically.
"""

from pathlib import Path
from research_assistant.config import Config
from research_assistant.workflow import ResearchWorkflow


def example_basic_usage():
    """Example: Basic research workflow."""
    print("=" * 60)
    print("Example 1: Basic Research")
    print("=" * 60)
    
    # Create configuration
    config = Config(
        max_search_results=10,
        max_papers_to_analyze=5,
        output_dir=Path("research_output")
    )
    
    # Create workflow
    workflow = ResearchWorkflow(config)
    
    # Run research (this would work with internet access)
    # report = workflow.run("quantum computing applications")
    
    # Access results
    # print(f"Topic: {report.topic}")
    # print(f"\nSummary:\n{report.summary}")
    # print(f"\nKey Findings:")
    # for finding in report.key_findings:
    #     print(f"  - {finding}")
    
    print("\nNote: This example requires internet access to run.")
    print("The workflow will:")
    print("1. Search for papers using DuckDuckGo")
    print("2. Read and analyze the papers")
    print("3. Generate a comprehensive report")
    print("4. Save the report to the output directory")


def example_with_openai():
    """Example: Enhanced research with OpenAI."""
    print("\n" + "=" * 60)
    print("Example 2: Enhanced Research with OpenAI")
    print("=" * 60)
    
    # Create configuration with OpenAI API key
    config = Config(
        openai_api_key="your-api-key-here",  # Add your API key
        model_name="gpt-3.5-turbo",
        temperature=0.7,
        max_search_results=15,
        max_papers_to_analyze=8,
        output_dir=Path("research_output")
    )
    
    # Create workflow
    workflow = ResearchWorkflow(config)
    
    # Run research (with enhanced AI-generated summaries)
    # report = workflow.run("artificial intelligence ethics")
    
    print("\nNote: With OpenAI API key, reports include:")
    print("  - AI-generated executive summaries")
    print("  - Detailed analysis with structured insights")
    print("  - Extracted key findings")
    print("  - Professional markdown formatting")


def example_custom_agents():
    """Example: Using individual agents."""
    print("\n" + "=" * 60)
    print("Example 3: Using Individual Agents")
    print("=" * 60)
    
    from research_assistant.agents.search_agent import WebSearchAgent
    from research_assistant.agents.reader_agent import PaperReadingAgent
    from research_assistant.agents.writer_agent import ReportWritingAgent
    
    # Initialize agents
    search_agent = WebSearchAgent(max_results=5)
    reader_agent = PaperReadingAgent()
    writer_agent = ReportWritingAgent()
    
    # Use search agent (requires internet)
    # results = search_agent.search_papers("machine learning")
    
    # Use reader agent (requires internet)
    # content = reader_agent.read_paper("https://arxiv.org/pdf/example.pdf")
    
    # Use writer agent
    # report = writer_agent.write_report(
    #     topic="machine learning",
    #     search_results=[],
    #     paper_contents=[]
    # )
    
    print("\nNote: Each agent can be used independently:")
    print("  - WebSearchAgent: Searches for papers and articles")
    print("  - PaperReadingAgent: Reads and extracts content from PDFs")
    print("  - ReportWritingAgent: Generates comprehensive reports")


def example_cli_usage():
    """Example: Command-line interface usage."""
    print("\n" + "=" * 60)
    print("Example 4: CLI Usage")
    print("=" * 60)
    
    print("\nBasic research:")
    print("  $ research-assistant research 'quantum computing'")
    
    print("\nWith custom options:")
    print("  $ research-assistant research 'AI in healthcare' \\")
    print("      --max-results 20 \\")
    print("      --max-papers 10 \\")
    print("      --output-dir my_research")
    
    print("\nSetup configuration:")
    print("  $ research-assistant setup")
    
    print("\nView information:")
    print("  $ research-assistant info")
    
    print("\nWith verbose logging:")
    print("  $ research-assistant research 'topic' --verbose")


if __name__ == "__main__":
    example_basic_usage()
    example_with_openai()
    example_custom_agents()
    example_cli_usage()
    
    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)
    print("\nFor more information, visit:")
    print("https://github.com/UserNJK/ResearchAssistant")
