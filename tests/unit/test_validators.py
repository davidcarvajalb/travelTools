"""Tests for validator utilities."""

from pathlib import Path

import pytest

from travel_tools.utils.validators import validate_file_exists


def test_validate_file_exists_accepts_existing_file(tmp_path: Path) -> None:
    file_path = tmp_path / "data.json"
    file_path.write_text("{}")
    validate_file_exists(file_path)  # Should not raise


def test_validate_file_exists_raises_for_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        validate_file_exists(tmp_path / "missing.json")


def test_validate_file_exists_rejects_directory(tmp_path: Path) -> None:
    directory = tmp_path / "folder"
    directory.mkdir()
    with pytest.raises(ValueError):
        validate_file_exists(directory)
