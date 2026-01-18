# API Documentation

This document describes how to use Research Assistant programmatically in your Python projects.

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Core Components](#core-components)
4. [Usage Examples](#usage-examples)
5. [API Reference](#api-reference)

## Installation

```bash
# Install PDM if necessary
pip install --user pdm

# Install dependencies and set up the project
pdm install

# Install package in development mode (editable)
pdm develop
```

Or add the project as a dependency via VCS using PDM:
```
pdm add git+https://github.com/UserNJK/ResearchAssistant.git
```

## Configuration

### Using Environment Variables

```python
from research_assistant.config import Config

# Load from environment variables
config = Config.from_env()
```

### Direct Configuration

```python
from pathlib import Path
from research_assistant.config import Config

config = Config(
    openai_api_key="your-api-key",  # Optional
    max_search_results=10,
    max_papers_to_analyze=5,
    output_dir=Path("research_output"),
    model_name="gpt-3.5-turbo",
    temperature=0.7
)
```

## Core Components

### 1. ResearchWorkflow

Main orchestration class that coordinates all agents.

```python
from research_assistant.workflow import ResearchWorkflow
from research_assistant.config import Config

config = Config.from_env()
workflow = ResearchWorkflow(config)

# Run research
report = workflow.run("quantum computing")

# Access results
print(report.topic)
print(report.summary)
print(report.key_findings)
print(report.full_text)
```

### 2. WebSearchAgent

Searches for papers and articles using DuckDuckGo.

```python
from research_assistant.agents.search_agent import WebSearchAgent

agent = WebSearchAgent(max_results=10)

# Search for papers
results = agent.search_papers("machine learning")

# General web search
results = agent.search_general("neural networks")

# Access results
for result in results:
    print(f"Title: {result.title}")
    print(f"URL: {result.url}")
    print(f"Snippet: {result.snippet}")
```

### 3. PaperReadingAgent

Reads and extracts content from PDFs and web pages.

```python
from research_assistant.agents.reader_agent import PaperReadingAgent

agent = PaperReadingAgent(timeout=30)

# Read a paper
content = agent.read_paper("https://arxiv.org/pdf/example.pdf")

if content.success:
    print(f"Title: {content.title}")
    print(f"Abstract: {content.abstract}")
    print(f"Pages: {content.num_pages}")
    print(f"Text: {content.text[:500]}")
else:
    print(f"Error: {content.error}")
```

### 4. ReportWritingAgent

Generates comprehensive research reports.

```python
from research_assistant.agents.writer_agent import ReportWritingAgent

agent = ReportWritingAgent(
    model_name="gpt-3.5-turbo",
    temperature=0.7,
    api_key="your-api-key"  # Optional
)

# Write report
report = agent.write_report(
    topic="artificial intelligence",
    search_results=[
        {
            'title': 'Paper 1',
            'url': 'http://example.com/paper1',
            'snippet': 'This paper discusses...'
        }
    ],
    paper_contents=[
        {
            'title': 'Paper 1',
            'text': 'Full text of the paper...',
            'abstract': 'Abstract of the paper...'
        }
    ]
)

print(report.summary)
print(report.detailed_analysis)
```

## Usage Examples

### Example 1: Basic Research

```python
from research_assistant.config import Config
from research_assistant.workflow import ResearchWorkflow

# Configure
config = Config(max_search_results=10, max_papers_to_analyze=5)

# Create workflow
workflow = ResearchWorkflow(config)

# Run research
report = workflow.run("quantum computing applications")

# Save to custom location
with open("my_report.md", "w") as f:
    f.write(report.full_text)
```

### Example 2: Using Individual Agents

```python
from research_assistant.agents.search_agent import WebSearchAgent
from research_assistant.agents.reader_agent import PaperReadingAgent
from research_assistant.agents.writer_agent import ReportWritingAgent

# Initialize agents
search_agent = WebSearchAgent(max_results=5)
reader_agent = PaperReadingAgent()
writer_agent = ReportWritingAgent()

# Search
search_results = search_agent.search_papers("neural networks")

# Read papers
paper_contents = []
for result in search_results[:3]:
    content = reader_agent.read_paper(result.url)
    if content.success:
        paper_contents.append({
            'title': content.title,
            'text': content.text,
            'abstract': content.abstract
        })

# Write report
search_dicts = [
    {
        'title': r.title,
        'url': r.url,
        'snippet': r.snippet
    }
    for r in search_results
]

report = writer_agent.write_report(
    topic="neural networks",
    search_results=search_dicts,
    paper_contents=paper_contents
)

print(report.full_text)
```

### Example 3: Custom Processing

```python
from research_assistant.workflow import ResearchWorkflow
from research_assistant.config import Config

# Custom configuration
config = Config(
    max_search_results=20,
    max_papers_to_analyze=10,
    output_dir=Path("my_research"),
    temperature=0.5  # More deterministic
)

workflow = ResearchWorkflow(config)
report = workflow.run("climate change mitigation")

# Process results
print(f"Found {len(report.references)} sources")
print(f"Generated {len(report.key_findings)} key findings")

# Filter findings
important_findings = [
    f for f in report.key_findings
    if "significant" in f.lower() or "important" in f.lower()
]
```

### Example 4: Batch Processing

```python
from research_assistant.workflow import ResearchWorkflow
from research_assistant.config import Config

config = Config(max_search_results=5, max_papers_to_analyze=3)
workflow = ResearchWorkflow(config)

topics = [
    "quantum computing",
    "machine learning",
    "blockchain technology"
]

reports = {}
for topic in topics:
    print(f"Researching: {topic}")
    report = workflow.run(topic)
    reports[topic] = report

# Compare reports
for topic, report in reports.items():
    print(f"\n{topic}:")
    print(f"  Key Findings: {len(report.key_findings)}")
    print(f"  References: {len(report.references)}")
```

## API Reference

### Config Class

#### Attributes

- `openai_api_key` (Optional[str]): OpenAI API key
- `max_search_results` (int): Maximum search results (default: 10)
- `max_papers_to_analyze` (int): Maximum papers to read (default: 5)
- `output_dir` (Path): Output directory (default: "research_output")
- `model_name` (str): LLM model name (default: "gpt-3.5-turbo")
- `temperature` (float): Generation temperature (default: 0.7)

#### Methods

- `from_env()`: Create config from environment variables

### SearchResult Class

#### Attributes

- `title` (str): Result title
- `url` (str): Result URL
- `snippet` (str): Result snippet/description
- `source` (str): Search source

### PaperContent Class

#### Attributes

- `url` (str): Paper URL
- `title` (str): Paper title
- `text` (str): Extracted text
- `abstract` (Optional[str]): Paper abstract
- `num_pages` (Optional[int]): Number of pages
- `success` (bool): Whether extraction succeeded
- `error` (Optional[str]): Error message if failed

### ResearchReport Class

#### Attributes

- `topic` (str): Research topic
- `summary` (str): Executive summary
- `detailed_analysis` (str): Detailed analysis
- `key_findings` (List[str]): List of key findings
- `references` (List[str]): List of reference URLs
- `full_text` (str): Complete report in Markdown

### WebSearchAgent

#### Methods

- `__init__(max_results: int = 10)`: Initialize agent
- `search(query: str) -> List[SearchResult]`: Search the web
- `search_papers(topic: str) -> List[SearchResult]`: Search for papers
- `search_general(query: str) -> List[SearchResult]`: General web search

### PaperReadingAgent

#### Methods

- `__init__(timeout: int = 30)`: Initialize agent
- `read_paper(url: str) -> PaperContent`: Read paper from URL

### ReportWritingAgent

#### Methods

- `__init__(model_name: str, temperature: float, api_key: Optional[str])`: Initialize agent
- `write_report(topic: str, search_results: List[Dict], paper_contents: List[Dict]) -> ResearchReport`: Generate report

### ResearchWorkflow

#### Methods

- `__init__(config: Config)`: Initialize workflow
- `run(topic: str) -> ResearchReport`: Execute research workflow

## Error Handling

```python
from research_assistant.workflow import ResearchWorkflow
from research_assistant.config import Config

config = Config.from_env()
workflow = ResearchWorkflow(config)

try:
    report = workflow.run("quantum computing")
except Exception as e:
    print(f"Research failed: {e}")
    # Handle error
```

## Best Practices

1. **Use Configuration**: Always use the Config class for settings
2. **Error Handling**: Wrap API calls in try-except blocks
3. **Rate Limiting**: Be mindful of API rate limits when making many requests
4. **Caching**: Consider caching search results for repeated queries
5. **Resource Management**: Clean up temporary files and resources
6. **Logging**: Enable logging for debugging

## Troubleshooting

### Import Errors

```python
# If you get import errors, ensure the package is installed
import sys
print(sys.path)  # Check Python path

# Reinstall if needed
# pip install -e .
```

### Network Issues

```python
# Increase timeout for slow connections
from research_assistant.agents.reader_agent import PaperReadingAgent

agent = PaperReadingAgent(timeout=60)  # Increase to 60 seconds
```

### Memory Issues

```python
# Reduce batch size for large research projects
config = Config(
    max_search_results=5,  # Reduce from default 10
    max_papers_to_analyze=2  # Reduce from default 5
)
```

## Additional Resources

- [README](README.md) - Project overview
- [QUICKSTART](QUICKSTART.md) - Quick start guide
- [CONTRIBUTING](CONTRIBUTING.md) - Contributing guidelines
- [Examples](examples.py) - Example scripts
