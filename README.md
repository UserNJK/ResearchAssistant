# Research Assistant 🔬🤖

An AI-powered research assistant that searches the web, reads papers, and generates comprehensive research reports - **completely free to use!**

## ✨ Features

- 🔍 **Web Search**: Automatically searches for research papers and articles using DuckDuckGo (no API key needed)
- 📄 **Paper Reading**: Extracts and analyzes content from PDF papers and web pages
- 📝 **Report Generation**: Creates comprehensive research reports with summaries and key findings
- 🆓 **Free to Use**: Works without any paid API keys (optional OpenAI integration for enhanced reports)
- 🎯 **Agentic AI**: Uses LangGraph to orchestrate multiple specialized agents
- 💻 **CLI Interface**: Easy-to-use command-line interface with beautiful output

## 🚀 Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/UserNJK/ResearchAssistant.git
cd ResearchAssistant
```

2. Install dependencies with PDM (preferred):
```bash
# Install PDM if you don't have it yet
pip install --user pdm

# Install project dependencies and create a local environment
pdm install
```

3. Install the package for development (make the CLI entrypoint available):
```bash
pdm develop
# Run the CLI via: pdm run research-assistant research "your topic"
```

### Basic Usage

Run a research query:
```bash
research-assistant research "quantum computing applications"
```

That's it! The tool will:
1. Search for relevant papers and articles
2. Read and analyze the content
3. Generate a comprehensive report
4. Save the report to the `research_output` directory

### Configuration (Optional)

For enhanced reports with AI-generated summaries, you can add an OpenAI API key:

1. Create a `.env` file:
```bash
research-assistant setup
```

2. Edit the `.env` file and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

**Note**: The tool works perfectly fine without an API key - it will just create structured reports without AI-generated summaries.

## 📖 Usage Examples

### Basic Research
```bash
research-assistant research "machine learning in healthcare"
```

### Advanced Research
```bash
research-assistant research "climate change mitigation" --max-papers 10 --max-results 20
```

### Custom Output Directory
```bash
research-assistant research "neural networks" --output-dir my_research
```

## 🎯 How It Works

The Research Assistant uses an agentic AI workflow powered by LangGraph:

1. **Search Agent**: Uses DuckDuckGo to find relevant papers and articles
2. **Reader Agent**: Extracts content from PDFs and web pages
3. **Writer Agent**: Synthesizes information into a comprehensive report

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Search    │────▶│ Read Papers  │────▶│ Write Report │
│   Agent     │     │    Agent     │     │    Agent     │
└─────────────┘     └──────────────┘     └──────────────┘
```

## 🛠️ Architecture

```
ResearchAssistant/
├── src/research_assistant/
│   ├── agents/
│   │   ├── search_agent.py    # Web search using DuckDuckGo
│   │   ├── reader_agent.py    # PDF and webpage reading
│   │   └── writer_agent.py    # Report generation
│   ├── utils/
│   │   └── helpers.py         # Utility functions
│   ├── config.py              # Configuration management
│   ├── workflow.py            # LangGraph workflow orchestration
│   └── cli.py                 # Command-line interface
├── requirements.txt
├── setup.py
└── README.md
```

## 📚 Technologies Used

- **LangGraph**: For orchestrating the multi-agent workflow
- **LangChain**: For LLM interactions and chains
- **DuckDuckGo Search**: Free web search API
- **pypdf**: For PDF parsing and extraction
- **BeautifulSoup**: For web scraping
- **Rich**: For beautiful CLI output
- **Click**: For command-line interface

## 🎨 Sample Output

When you run a research query, you'll get:

- **Executive Summary**: Concise overview of the research topic
- **Key Findings**: Bullet points of important discoveries
- **Detailed Analysis**: In-depth analysis from multiple sources
- **References**: All sources used in the research
- **Markdown Report**: Saved to file for future reference

## ⚙️ Configuration Options

You can customize the behavior using environment variables or command-line options:

| Option | Default | Description |
|--------|---------|-------------|
| `MAX_SEARCH_RESULTS` | 10 | Maximum number of search results |
| `MAX_PAPERS_TO_ANALYZE` | 5 | Maximum papers to read in detail |
| `OUTPUT_DIR` | research_output | Output directory for reports |
| `MODEL_NAME` | gpt-3.5-turbo | LLM model (if using OpenAI) |
| `TEMPERATURE` | 0.7 | Generation temperature |

## 🔧 Advanced Usage

### Using as a Python Library

```python
from research_assistant.config import Config
from research_assistant.workflow import ResearchWorkflow

# Create configuration
config = Config.from_env()

# Create workflow
workflow = ResearchWorkflow(config)

# Run research
report = workflow.run("artificial intelligence ethics")

# Access results
print(report.summary)
print(report.key_findings)
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com/) and [LangGraph](https://github.com/langchain-ai/langgraph)
- Uses [DuckDuckGo](https://duckduckgo.com/) for free web search
- Inspired by the need for accessible research tools

## 📞 Support

For issues and questions, please open an issue on GitHub.

---

**Made with ❤️ for researchers, students, and curious minds everywhere!**
