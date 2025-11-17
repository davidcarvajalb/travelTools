"""Step 3.5: Normalize merged data for web output."""

from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import click

from .utils.file_ops import load_json, save_json
from .utils.logger import console
from .utils.validators import validate_file_exists

MEAL_PLAN_LABELS = {
    "AI": "All Inclusive",
    "EP": "European Plan (no meals)",
}


def normalize_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        if value in (1, 2):
            return True
        if value == 0:
            return False
    return None


def normalize_int(value: Any) -> int | None:
    try:
        if value is None or value == "":
            return None
        num = int(value)
        if num <= 0:
            return None
        return num
    except Exception:
        return None


def normalize_thumbnail(url: str | None) -> str | None:
    if not url:
        return None
    parsed = urlparse(url)
    if not parsed.scheme:
        if url.startswith("//"):
            return f"https:{url}"
        return f"https://{url.lstrip('/')}"
    if parsed.scheme != "https":
        return url.replace(f"{parsed.scheme}://", "https://", 1)
    return url


def normalize_meal_plan(code: str | None) -> tuple[str | None, str | None]:
    if not code:
        return None, None
    label = MEAL_PLAN_LABELS.get(code)
    return code, label


def normalize_hotel(hotel: dict, stats: Counter) -> dict:
    hotel = dict(hotel)  # Shallow copy

    hotel["drinks24h"] = normalize_bool(hotel.get("drinks24h"))
    hotel["snacks24h"] = normalize_bool(hotel.get("snacks24h"))

    if hotel["drinks24h"] is None:
        stats["drinks24h_null"] += 1
    if hotel["snacks24h"] is None:
        stats["snacks24h_null"] += 1

    hotel["number_of_restaurants"] = normalize_int(hotel.get("number_of_restaurants"))
    if hotel["number_of_restaurants"] is None:
        stats["number_of_restaurants_null"] += 1

    spa_available = hotel.get("spa_available")
    if spa_available in ("", None):
        hotel["spa_available"] = None
        stats["spa_available_null"] += 1

    code, label = normalize_meal_plan(hotel.get("meal_plan_code"))
    hotel["meal_plan_code"] = code
    hotel["meal_plan_label"] = label
    if code is None:
        stats["meal_plan_missing"] += 1
    if label is None:
        stats["meal_plan_unknown"] += 1

    hotel["thumbnail_url"] = normalize_thumbnail(
        hotel.get("thumbnail_url")
        or (hotel.get("thumbnailPath") if "thumbnailPath" in hotel else None)
    )
    if hotel["thumbnail_url"] is None:
        stats["thumbnail_missing"] += 1

    normalized_packages = []
    for pkg in hotel.get("packages", []):
        pkg = dict(pkg)
        pkg["drinks24h"] = normalize_bool(pkg.get("drinks24h"))
        pkg["snacks24h"] = normalize_bool(pkg.get("snacks24h"))
        pkg["number_of_restaurants"] = normalize_int(pkg.get("number_of_restaurants"))
        pkg_spa = pkg.get("spa_available")
        if pkg_spa in ("", None):
            pkg["spa_available"] = None
        pkg_code, pkg_label = normalize_meal_plan(pkg.get("meal_plan_code"))
        pkg["meal_plan_code"] = pkg_code
        pkg["meal_plan_label"] = pkg_label
        pkg["thumbnail_url"] = normalize_thumbnail(pkg.get("thumbnail_url"))
        normalized_packages.append(pkg)

    hotel["packages"] = normalized_packages
    return hotel


@click.command()
@click.option("--destination", required=True, type=str, help="Destination slug")
@click.option("--source", required=True, type=str, help="Source slug")
def main(destination: str, source: str) -> None:
    """Normalize merged data for downstream consumption."""
    merged_file = Path(f"data/{destination}/{source}/merged/final_data.json")
    output_file = Path(f"data/{destination}/{source}/normalized/final_data.json")

    try:
        validate_file_exists(merged_file)
        merged = load_json(merged_file)

        stats: Counter[str] = Counter()
        normalized = [normalize_hotel(hotel, stats) for hotel in merged]

        output_file.parent.mkdir(parents=True, exist_ok=True)
        save_json(normalized, output_file)

        console.print(f"[green]✓[/green] Normalized {len(normalized)} hotels")
        if stats:
            console.print("[blue]Normalization notes:[/blue]")
            for key, val in sorted(stats.items()):
                console.print(f"  {key}: {val}")
        console.print(f"[blue]Output:[/blue] {output_file}")
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


if __name__ == "__main__":
    main()
