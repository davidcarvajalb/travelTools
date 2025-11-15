"""Step 1: Filter packages by budget."""

import json
from pathlib import Path

import click

from .types import HotelPackage
from .utils.file_ops import ensure_dir, load_json, save_json
from .utils.logger import console
from .utils.validators import validate_file_exists


def transform_transat_package(transat_pkg: dict) -> dict:
    """Transform Transat package format to our standard format.

    Args:
        transat_pkg: Package dict from Transat API

    Returns:
        Transformed package dict matching HotelPackage model
    """
    hotel = transat_pkg.get('hotel', {})

    # Build amenities list
    amenities = []
    if transat_pkg.get('mealPlanCode') == 'AI':
        amenities.append('All-Inclusive')
    if hotel.get('adultOnly') == 1:
        amenities.append('Adults Only')
    if hotel.get('drinks24h') == 1:
        amenities.append('24h Drinks')
    if hotel.get('snacks24h') == 1:
        amenities.append('24h Snacks')
    num_restaurants = hotel.get('numberOfRestaurants', 0)
    if num_restaurants > 0:
        amenities.append(f'{num_restaurants} Restaurants')

    # Use totalPriceForGroup as the price (for 2 adults typically)
    price = transat_pkg.get('totalPriceForGroup', 0)

    # Convert stars to int (Transat sometimes has 4.5 stars)
    stars = hotel.get('transatStars')
    if stars is not None:
        stars = int(round(stars))

    return {
        'hotel_name': hotel.get('name', 'Unknown Hotel'),
        'city': hotel.get('city', 'Unknown'),
        'stars': stars,
        'room_type': transat_pkg.get('mealPlanCode', 'Standard'),  # Using meal plan as room type for now
        'url': hotel.get('url'),
        'drinks24h': hotel.get('drinks24h') == 1,
        'snacks24h': hotel.get('snacks24h') == 1,
        'adult_only': hotel.get('adultOnly', 0),
        'amenities': amenities,
        'price': float(price),
        'dates': {
            'departure': transat_pkg.get('departureDate', ''),
            'return': transat_pkg.get('returnDate', '')
        }
    }


def filter_packages(packages_data: list[dict], budget: float) -> list[dict]:
    """Filter packages by maximum budget.

    Args:
        packages_data: List of package dictionaries (Transat format)
        budget: Maximum price threshold

    Returns:
        List of filtered package dictionaries (standard format)
    """
    # Transform and filter
    filtered = []
    for pkg_data in packages_data:
        try:
            # Transform Transat format to our format
            transformed = transform_transat_package(pkg_data)

            # Validate with Pydantic
            pkg = HotelPackage(**transformed)

            # Filter by budget
            if pkg.price <= budget:
                filtered.append(pkg.model_dump(by_alias=True))
        except Exception as e:
            console.print(f"[yellow]Warning:[/yellow] Skipping invalid package: {e}")
            continue

    return filtered


@click.command()
@click.option("--destination", required=True, type=str, help="Destination name (e.g., cancun)")
@click.option("--source", required=True, type=str, help="Package source (e.g., transat)")
@click.option("--budget", required=True, type=float, help="Maximum budget in CAD")
def main(destination: str, source: str, budget: float) -> None:
    """Filter hotel packages by maximum budget."""
    # Paths
    input_path = Path(f"data/{destination}/{source}/raw/packages.json")
    output_path = Path(f"data/{destination}/{source}/filtered/budget_{int(budget)}.json")

    try:
        # Validate input
        validate_file_exists(input_path)

        # Load packages
        console.print(f"[blue]Loading packages from:[/blue] {input_path}")
        packages_raw = load_json(input_path)

        # Handle both formats: {"packages": [...]} or [...]
        if isinstance(packages_raw, dict):
            if "packages" in packages_raw:
                packages_raw = packages_raw["packages"]
                console.print(f"[blue]Extracted packages from nested structure[/blue]")
            else:
                raise ValueError("packages.json object must contain a 'packages' key")

        if not isinstance(packages_raw, list):
            raise ValueError("packages.json must contain a list of packages or an object with a 'packages' key")

        # Filter
        console.print(f"[blue]Filtering packages with budget:[/blue] ${budget:,.0f}")
        filtered = filter_packages(packages_raw, budget)

        # Save
        save_json(filtered, output_path)

        # Report
        console.print(
            f"[green]✓[/green] Filtered {len(packages_raw)} → {len(filtered)} packages"
        )
        console.print(f"[blue]Output:[/blue] {output_path}")

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        console.print(
            f"[yellow]Hint:[/yellow] Ensure raw packages exist at {input_path}"
        )
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


if __name__ == "__main__":
    main()
