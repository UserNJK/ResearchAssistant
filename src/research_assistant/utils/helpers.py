"""Utility functions for Research Assistant."""

import logging
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.logging import RichHandler


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Setup logging with Rich handler."""
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    return logging.getLogger("research_assistant")


def ensure_directory(path: Path) -> Path:
    """Ensure directory exists."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def create_console() -> Console:
    """Create Rich console for beautiful output."""
    return Console()


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to remove invalid characters."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename[:200]  # Limit filename length
