"""Setup script for Research Assistant."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="research-assistant",
    version="0.1.0",
    description="AI-powered research assistant for searching, reading, and analyzing research papers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Research Assistant Team",
    url="https://github.com/UserNJK/ResearchAssistant",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "langgraph>=0.2.0",
        "langchain>=0.1.0",
        "langchain-community>=0.0.20",
        "langchain-openai>=0.0.5",
        "ddgs>=1.0.0",
        "beautifulsoup4>=4.12.0",
        "requests>=2.31.0",
        "lxml>=4.9.0",
        "pypdf>=4.0.0",
        "python-docx>=1.1.0",
        "markdown>=3.5.0",
        "python-dotenv>=1.0.0",
        "click>=8.1.0",
        "rich>=13.0.0",
        "pydantic>=2.0.0",
        "tenacity>=8.2.0",
    ],
    entry_points={
        "console_scripts": [
            "research-assistant=research_assistant.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing",
    ],
    keywords="research, ai, papers, assistant, langchain, langgraph",
)
