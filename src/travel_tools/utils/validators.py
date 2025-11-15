"""Data validation utilities."""

from pathlib import Path


def validate_file_exists(path: Path) -> None:
    """Validate that a file exists."""
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")
