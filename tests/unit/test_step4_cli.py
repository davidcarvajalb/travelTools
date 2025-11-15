"""CLI tests for step4 (generate web)."""

import json
from pathlib import Path

from click.testing import CliRunner

from travel_tools.step3_merge import merge_data
from travel_tools.utils.file_ops import save_json
from travel_tools.step4_generate_web import main as step4_main


def test_step4_main_creates_output(tmp_path, sample_packages, sample_ratings, monkeypatch):
    """Run the CLI end-to-end using temporary data."""
    data_dir = tmp_path / "data" / "cancun" / "transat"
    merged_dir = data_dir / "merged"
    filtered_dir = data_dir / "filtered"
    merged_dir.mkdir(parents=True)
    filtered_dir.mkdir(parents=True)

    merged = merge_data(sample_packages, sample_ratings, source="transat")
    save_json(merged, merged_dir / "final_data.json")
    (filtered_dir / "budget_5000.json").write_text("[]")

    outputs_dir = tmp_path / "outputs"
    monkeypatch.chdir(tmp_path)

    runner = CliRunner()
    result = runner.invoke(step4_main, ["--destination", "cancun", "--source", "transat"])

    assert result.exit_code == 0
    output_file = outputs_dir / "cancun" / "transat" / "hotels.json"
    assert output_file.exists()
    payload = json.loads(output_file.read_text())
    assert payload["metadata"]["destination"] == "cancun"
