# Quick Start Guide

Get started with Research Assistant in 5 minutes!

## Installation

```bash
# Clone the repository
git clone https://github.com/UserNJK/ResearchAssistant.git
cd ResearchAssistant

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## Your First Research Query

```bash
research-assistant research "quantum computing"
```

That's it! The tool will:
1. 🔍 Search for papers and articles
2. 📄 Read and analyze content
3. 📝 Generate a comprehensive report
4. 💾 Save to `research_output/` directory

## Viewing Results

After the research completes, you'll see:
- **Summary** in the terminal
- **Key Findings** as bullet points
- **Full Report** saved as a Markdown file in `research_output/`

Open the report file to see:
- Executive summary
- Detailed analysis
- Key findings
- References with links

## Basic Commands

```bash
# Get help
research-assistant --help

# View information
research-assistant info

# Setup configuration (optional)
research-assistant setup

# Run research with options
research-assistant research "your topic" \
    --max-results 20 \
    --max-papers 10 \
    --output-dir my_research \
    --verbose
```

## Optional: Enhanced Reports with OpenAI

For AI-generated summaries and analysis:

1. Get an API key from [OpenAI](https://platform.openai.com/api-keys)
2. Run setup: `research-assistant setup`
3. Edit `.env` and add your key: `OPENAI_API_KEY=your-key-here`
4. Run research as normal

**Note**: The tool works great without OpenAI - reports will be structured but without AI-generated summaries.

## Tips

- Start with `--max-results 5 --max-papers 2` for quick tests
- Use `--verbose` to see detailed progress
- Check `research_output/` for saved reports
- Reports are in Markdown format - open with any text editor

## Example Topics to Try

```bash
research-assistant research "machine learning in healthcare"
research-assistant research "climate change mitigation strategies"
research-assistant research "blockchain technology applications"
research-assistant research "neural network architectures"
```

## Need Help?

- Run `research-assistant --help` for all options
- Check the [README](README.md) for detailed documentation
- Open an issue on [GitHub](https://github.com/UserNJK/ResearchAssistant/issues)

## Next Steps

- Explore the [full documentation](README.md)
- Learn about [contributing](CONTRIBUTING.md)
- Check out [examples.py](examples.py) for programmatic usage
