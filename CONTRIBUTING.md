# Contributing to Research Assistant

Thank you for considering contributing to Research Assistant! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/ResearchAssistant.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Install dependencies: `pip install -r requirements.txt`
5. Install in development mode: `pip install -e .`

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip
- git

### Installation

```bash
# Clone the repository
git clone https://github.com/UserNJK/ResearchAssistant.git
cd ResearchAssistant

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## Making Changes

### Code Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for all functions and classes
- Keep functions focused and modular

### Project Structure

```
ResearchAssistant/
├── src/research_assistant/
│   ├── agents/           # Agent implementations
│   ├── utils/            # Utility functions
│   ├── config.py         # Configuration management
│   ├── workflow.py       # Main workflow orchestration
│   └── cli.py           # CLI interface
├── requirements.txt
├── setup.py
└── README.md
```

### Adding New Features

1. **New Agents**: Add new agent classes in `src/research_assistant/agents/`
2. **Utilities**: Add helper functions in `src/research_assistant/utils/`
3. **CLI Commands**: Extend the CLI in `src/research_assistant/cli.py`
4. **Workflow Changes**: Modify the workflow in `src/research_assistant/workflow.py`

## Testing

Before submitting a pull request, ensure your changes work correctly:

```bash
# Test the CLI
research-assistant info
research-assistant --help

# Test with a simple research query (if you have internet access)
research-assistant research "test topic" --max-results 3 --max-papers 1
```

## Submitting Changes

1. Commit your changes: `git commit -m "Add feature: description"`
2. Push to your fork: `git push origin feature/your-feature-name`
3. Create a Pull Request on GitHub

### Pull Request Guidelines

- Provide a clear description of the changes
- Reference any related issues
- Ensure the code follows the project's style guidelines
- Update documentation if necessary

## Areas for Contribution

### High Priority

- Add more search backends (Google Scholar, Semantic Scholar, etc.)
- Implement caching for search results and paper contents
- Add support for more document formats (Word, HTML, etc.)
- Improve error handling and retry logic
- Add unit tests and integration tests

### Medium Priority

- Add support for more LLM providers (Anthropic, Hugging Face, etc.)
- Implement concurrent paper reading for better performance
- Add progress bars and better user feedback
- Create a web interface
- Add citation management features

### Low Priority

- Add visualization of research findings
- Implement paper recommendation system
- Add collaboration features
- Create mobile app

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## Questions?

If you have questions about contributing, please open an issue on GitHub.

## License

By contributing to Research Assistant, you agree that your contributions will be licensed under the MIT License.
