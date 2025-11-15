"""Step 4: Generate web viewer JSON from merged data."""

from datetime import datetime
from pathlib import Path

import click
from .types import WebHotel, WebMetadata, WebOutput, WebPackage
from .utils.file_ops import load_json, save_json
from .utils.logger import console
from .utils.validators import validate_file_exists


def transform_to_web_format(
    merged_data: list[dict], destination: str, source: str, budget: int
) -> dict:
    """Transform merged data to web output format.

    Args:
        merged_data: List of merged hotel dictionaries
        destination: Destination name
        source: Package source name
        budget: Budget used for filtering

    Returns:
        Dictionary with metadata and hotels in web format
    """
    web_hotels = []

    for idx, hotel in enumerate(merged_data):
        # Transform packages
        web_packages = []
        for pkg in hotel.get("packages", []):
            try:
                # Parse dates
                dep_date = pkg["dates"]["departure"]
                ret_date = pkg["dates"]["return"]

                # Handle both datetime objects and strings
                if isinstance(dep_date, str):
                    dep_dt = datetime.fromisoformat(dep_date.replace("Z", "+00:00"))
                else:
                    dep_dt = dep_date

                if isinstance(ret_date, str):
                    ret_dt = datetime.fromisoformat(ret_date.replace("Z", "+00:00"))
                else:
                    ret_dt = ret_date

                duration_days = (ret_dt - dep_dt).days

                web_pkg = WebPackage(
                    departure=dep_dt.strftime("%Y-%m-%d"),
                    return_date=ret_dt.strftime("%Y-%m-%d"),
                    duration_days=duration_days,
                    room_type=pkg.get("room_type", "Standard"),
                    price=pkg.get("price", 0),
                    url=pkg.get("url"),
                    drinks24h=bool(pkg.get("drinks24h")),
                    snacks24h=bool(pkg.get("snacks24h")),
                )
                web_packages.append(web_pkg)
            except Exception as e:
                console.print(f"[yellow]Warning:[/yellow] Skipping invalid package: {e}")
                continue

        # Create web hotel
        web_hotel = WebHotel(
            id=f"hotel_{idx:03d}",
            name=hotel["name"],
            city=hotel["city"],
            stars=hotel.get("stars"),
            google_rating=hotel.get("google_rating"),
            review_count=hotel.get("review_count"),
            air_transat_url=hotel.get("air_transat_url"),
            google_maps_url=hotel.get("google_maps_url"),
            drinks24h=hotel.get("drinks24h", False),
            snacks24h=hotel.get("snacks24h", False),
            adult_only=hotel.get("adult_only"),
            departure_date=hotel.get("departure_date"),
            return_date=hotel.get("return_date"),
            price_range=hotel["price_range"],
            package_count=len(web_packages),
            packages=web_packages,
        )
        web_hotels.append(web_hotel)

    # Create metadata
    metadata = WebMetadata(
        destination=destination,
        source=source,
        generated_at=datetime.now().isoformat(),
        budget=budget,
        total_hotels=len(web_hotels),
    )

    # Create output
    output = WebOutput(metadata=metadata, hotels=web_hotels)

    return output.model_dump(by_alias=True)


@click.command()
@click.option("--destination", required=True, type=str, help="Destination name")
@click.option("--source", required=True, type=str, help="Package source")
def main(destination: str, source: str) -> None:
    """Generate JSON payload used by the Vue web viewer."""
    # Paths
    merged_file = Path(f"data/{destination}/{source}/merged/final_data.json")
    filtered_dir = Path(f"data/{destination}/{source}/filtered")
    output_dir = Path(f"outputs/{destination}/{source}")
    json_output = output_dir / "hotels.json"

    try:
        # Validate
        validate_file_exists(merged_file)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Get budget from filtered file
        budget = 5000  # default
        if filtered_dir.exists():
            filtered_files = list(filtered_dir.glob("budget_*.json"))
            if filtered_files:
                latest_filtered = max(filtered_files, key=lambda p: p.stat().st_mtime)
                budget = int(latest_filtered.stem.split("_")[1])

        # Load merged data
        console.print(f"[blue]Loading merged data from:[/blue] {merged_file}")
        merged_data = load_json(merged_file)

        # Transform to web format
        console.print("[blue]Transforming data for web viewer...[/blue]")
        web_data = transform_to_web_format(merged_data, destination, source, budget)

        # Save JSON
        save_json(web_data, json_output)
        console.print(f"[green]✓[/green] Saved JSON data: {json_output}")

        console.print(
            "\n[blue]Next steps:[/blue] Build the Vue viewer in `web_client/` and serve "
            "the contents of the outputs directory."
        )
        console.print(
            "[blue]Example:[/blue] cd web_client && npm install && npm run build "
            "&& cd ../outputs && python -m http.server 8000"
        )
        console.print(
            "[blue]Then visit:[/blue] http://localhost:8000/viewer/ to pick a destination."
        )

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        import traceback

        traceback.print_exc()
        raise click.Abort()


if __name__ == "__main__":
    main()
