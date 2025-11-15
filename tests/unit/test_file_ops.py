"""Tests for file operations."""

from datetime import datetime
from pathlib import Path

import json
import pytest

from travel_tools.utils.file_ops import (
    DateTimeEncoder,
    ensure_dir,
    load_json,
    save_json,
)


def test_datetime_encoder_serializes_isoformat():
    data = {"timestamp": datetime(2024, 1, 1, 12, 0, 0)}
    encoded = json.dumps(data, cls=DateTimeEncoder)
    assert '"timestamp": "2024-01-01T12:00:00"' in encoded


def test_ensure_dir_creates_path(tmp_path: Path):
    target = tmp_path / "nested" / "dir"
    ensure_dir(target)
    assert target.exists()
    assert target.is_dir()


def test_save_and_load_json(tmp_path: Path):
    path = tmp_path / "data" / "output.json"
    payload = {"value": 42}
    save_json(payload, path)
    assert path.exists()
    loaded = load_json(path)
    assert loaded == payload
