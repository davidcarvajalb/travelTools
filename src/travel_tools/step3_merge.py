"""Step 3: Merge filtered packages with Google ratings."""

from collections import defaultdict
from pathlib import Path
from statistics import mean
from urllib.parse import quote_plus

import click

from .types import HotelData, HotelPackage, PriceRange, ReviewSummary
from .utils.file_ops import load_json, save_json
from .utils.logger import console
from .utils.validators import validate_file_exists


def merge_data(
    packages_data: list[dict], ratings_data: list[dict], source: str
) -> list[dict]:
    """Merge packages with ratings.

    Args:
        packages_data: List of package dictionaries
        ratings_data: List of rating dictionaries
        source: Package source name

    Returns:
        List of merged hotel data dictionaries
    """
    # Create ratings lookup
    ratings_map = {r["hotel_name"]: r for r in ratings_data}

    # Group packages by hotel
    hotels_packages: dict[str, list[dict]] = defaultdict(list)
    for pkg in packages_data:
        hotels_packages[pkg["hotel_name"]].append(pkg)

    # Merge
    merged = []
    for hotel_name, hotel_pkgs in hotels_packages.items():
        # Get rating data
        rating_info = ratings_map.get(hotel_name, {})
        summary_payload = rating_info.get("review_summary")
        review_summary = None
        if isinstance(summary_payload, dict):
            try:
                review_summary = ReviewSummary(**summary_payload)
            except Exception as e:
                console.print(
                    f"[yellow]Warning:[/yellow] Skipping invalid review summary for {hotel_name}: {e}"
                )

        # Calculate price range
        prices = [pkg["price"] for pkg in hotel_pkgs]

        # Parse packages
        packages = []
        for pkg_data in hotel_pkgs:
            try:
                pkg = HotelPackage(**pkg_data)
                packages.append(pkg)
            except Exception as e:
                console.print(f"[yellow]Warning:[/yellow] Invalid package for {hotel_name}: {e}")

        if not packages:
            continue

        air_transat_url = next((pkg.url for pkg in packages if pkg.url), None)
        drinks24h = any(pkg.drinks24h for pkg in packages)
        snacks24h = any(pkg.snacks24h for pkg in packages)
        adult_values = [pkg.adult_only for pkg in packages if pkg.adult_only is not None]
        adult_only = adult_values[0] if adult_values else None
        number_of_restaurants = next(
            (pkg.number_of_restaurants for pkg in packages if pkg.number_of_restaurants is not None),
            None,
        )
        spa_available = next(
            (pkg.spa_available for pkg in packages if pkg.spa_available is not None),
            None,
        )
        meal_plan_code = next(
            (pkg.meal_plan_code for pkg in packages if pkg.meal_plan_code),
            None,
        )
        meal_plan_label = next(
            (pkg.meal_plan_label for pkg in packages if pkg.meal_plan_label),
            None,
        )
        thumbnail_url = next(
            (pkg.thumbnail_url for pkg in packages if pkg.thumbnail_url),
            None,
        )
        departure_date = (
            min(pkg.dates.departure for pkg in packages).isoformat()
            if packages
            else None
        )
        return_date = (
            max(pkg.dates.return_date for pkg in packages).isoformat()
            if packages
            else None
        )
        google_maps_url = f"https://www.google.com/maps/search/{quote_plus(hotel_name)}"

        # Create hotel data
        hotel_data = HotelData(
            name=hotel_name,
            city=packages[0].city,
            stars=packages[0].stars,
            google_rating=rating_info.get("rating"),
            review_count=rating_info.get("review_count"),
            air_transat_url=air_transat_url,
            google_maps_url=google_maps_url,
            drinks24h=drinks24h,
            snacks24h=snacks24h,
            adult_only=adult_only,
            number_of_restaurants=number_of_restaurants,
            spa_available=spa_available,
            meal_plan_code=meal_plan_code,
            meal_plan_label=meal_plan_label,
            thumbnail_url=thumbnail_url,
            departure_date=departure_date,
            return_date=return_date,
            source=source,
            price_range=PriceRange(min=min(prices), max=max(prices), avg=mean(prices)),
            packages=packages,
            review_summary=review_summary,
        )

        merged.append(hotel_data.model_dump(by_alias=True))

    return merged


@click.command()
@click.option("--destination", required=True, type=str, help="Destination name")
@click.option("--source", required=True, type=str, help="Package source")
@click.option(
    "--hotel",
    type=str,
    default=None,
    help="Only merge the hotel with this exact name (case-insensitive)",
)
def main(destination: str, source: str, hotel: str | None) -> None:
    """Merge filtered packages with Google ratings."""
    # Paths
    filtered_dir = Path(f"data/{destination}/{source}/filtered")
    summarized_ratings_file = Path(
        f"data/{destination}/{source}/scraped/ratings_with_summaries.json"
    )
    fallback_ratings_file = Path(
        f"data/{destination}/{source}/scraped/google_ratings.json"
    )
    output_path = Path(f"data/{destination}/{source}/merged/final_data.json")

    try:
        # Find filtered file
        if not filtered_dir.exists() or not list(filtered_dir.glob("*.json")):
            raise FileNotFoundError(f"No filtered packages found in {filtered_dir}")

        filtered_file = max(filtered_dir.glob("*.json"), key=lambda p: p.stat().st_mtime)

        # Validate
        validate_file_exists(filtered_file)

        ratings_file = (
            summarized_ratings_file if summarized_ratings_file.exists() else fallback_ratings_file
        )
        validate_file_exists(ratings_file)

        # Load data
        console.print(f"[blue]Loading packages from:[/blue] {filtered_file}")
        packages = load_json(filtered_file)
        if hotel:
            packages = [p for p in packages if p.get("hotel_name", "").lower() == hotel.lower()]
            console.print(f"[yellow]Filtering merge to hotel:[/yellow] {hotel}")

        console.print(f"[blue]Loading ratings from:[/blue] {ratings_file}")
        ratings = load_json(ratings_file)

        # Merge
        console.print("[blue]Merging data...[/blue]")
        merged = merge_data(packages, ratings, source)

        # Save
        save_json(merged, output_path)

        # Report
        console.print(f"[green]✓[/green] Merged {len(merged)} hotels")

        # Statistics
        with_ratings = sum(1 for h in merged if h.get("google_rating") is not None)
        console.print(f"[blue]Hotels with ratings:[/blue] {with_ratings}/{len(merged)}")
        console.print(f"[blue]Output:[/blue] {output_path}")

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


if __name__ == "__main__":
    main()
