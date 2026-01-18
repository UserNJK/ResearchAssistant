"""Command-line interface for Research Assistant."""

import click
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import Config
from .workflow import ResearchWorkflow
from .utils.helpers import setup_logging


console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Research Assistant - AI-powered research tool.
    
    Search the web, read papers, and generate comprehensive research reports.
    """
    pass


@cli.command()
@click.argument('topic')
@click.option('--max-results', default=10, help='Maximum search results')
@click.option('--max-papers', default=5, help='Maximum papers to analyze')
@click.option('--output-dir', default='research_output', help='Output directory')
@click.option('--verbose', is_flag=True, help='Enable verbose logging')
def research(topic: str, max_results: int, max_papers: int, output_dir: str, verbose: bool):
    """Conduct research on a given TOPIC.
    
    Examples:
    
        research-assistant research "quantum computing applications"
        
        research-assistant research "machine learning in healthcare" --max-papers 10
    """
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(log_level)
    
    # Create configuration
    config = Config.from_env()
    config.max_search_results = max_results
    config.max_papers_to_analyze = max_papers
    config.output_dir = Path(output_dir)
    
    # Display start message
    console.print(Panel.fit(
        f"[bold cyan]Research Assistant[/bold cyan]\n\n"
        f"Topic: [yellow]{topic}[/yellow]\n"
        f"Max Results: {max_results}\n"
        f"Max Papers: {max_papers}",
        border_style="cyan"
    ))
    
    # Create workflow
    workflow = ResearchWorkflow(config)
    
    # Run research with progress indicators
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task("[cyan]Conducting research...", total=None)
        
        try:
            report = workflow.run(topic)
            progress.update(task, completed=True)
            
            # Display results
            console.print("\n[bold green]✓ Research completed![/bold green]\n")
            
            console.print(Panel(
                report.summary,
                title="[bold]Summary[/bold]",
                border_style="green"
            ))
            
            console.print("\n[bold]Key Findings:[/bold]")
            for i, finding in enumerate(report.key_findings, 1):
                console.print(f"  {i}. {finding}")
            
            console.print(f"\n[bold]References:[/bold] {len(report.references)} sources")
            
            # Show save location
            console.print(f"\n[bold cyan]Report saved to:[/bold cyan] {config.output_dir}")
            
        except Exception as e:
            progress.update(task, completed=True)
            console.print(f"\n[bold red]✗ Error:[/bold red] {str(e)}")
            raise click.ClickException(str(e))


@cli.command()
def setup():
    """Setup the Research Assistant with configuration.
    
    Creates a .env file template for API keys and settings.
    """
    env_template = """# Research Assistant Configuration

# OpenAI API Key (optional - can work without it but with limited features)
# Get your key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# Search Settings
MAX_SEARCH_RESULTS=10
MAX_PAPERS_TO_ANALYZE=5

# Output Settings
OUTPUT_DIR=research_output

# Model Settings (if using OpenAI)
MODEL_NAME=gpt-3.5-turbo
TEMPERATURE=0.7
"""
    
    env_path = Path('.env')
    
    if env_path.exists():
        if not click.confirm('.env file already exists. Overwrite?'):
            console.print("[yellow]Setup cancelled.[/yellow]")
            return
    
    with open(env_path, 'w') as f:
        f.write(env_template)
    
    console.print(Panel.fit(
        "[bold green]✓ Setup complete![/bold green]\n\n"
        "A .env file has been created.\n"
        "Edit it to add your API keys and customize settings.\n\n"
        "[bold]Note:[/bold] The tool works without OpenAI API key,\n"
        "but reports will be more basic.",
        border_style="green"
    ))


@cli.command()
def info():
    """Display information about Research Assistant."""
    info_text = """[bold cyan]Research Assistant v0.1.0[/bold cyan]

An AI-powered research tool that:

• [green]Searches the web[/green] for research papers and articles
• [green]Reads and analyzes[/green] PDF papers and web content
• [green]Generates comprehensive reports[/green] with summaries and key findings

[bold]Features:[/bold]

• Free to use with DuckDuckGo search (no API key needed)
• Optional OpenAI integration for enhanced reports
• Supports PDF papers from arXiv and other sources
• Markdown formatted output
• Command-line interface

[bold]Usage:[/bold]

  research-assistant research "your topic"
  research-assistant setup
  research-assistant info

[bold]More info:[/bold] https://github.com/UserNJK/ResearchAssistant
"""
    console.print(Panel(info_text, border_style="cyan"))


def main():
    """Main entry point."""
    cli()


if __name__ == '__main__':
    main()
