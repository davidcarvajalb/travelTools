"""File operation utilities."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime objects."""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def ensure_dir(path: Path) -> None:
    """Create directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)


def load_json(path: Path) -> Any:
    """Load JSON file."""
    with open(path, "r") as f:
        return json.load(f)


def save_json(data: Any, path: Path, indent: int = 2) -> None:
    """Save data to JSON file."""
    ensure_dir(path.parent)
    with open(path, "w") as f:
        json.dump(data, f, indent=indent, cls=DateTimeEncoder)
