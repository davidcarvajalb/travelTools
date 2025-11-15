"""Step 2: Scrape hotel ratings from Google Maps."""

from datetime import datetime
from pathlib import Path
import re

import click
from playwright.sync_api import (
    Page,
    TimeoutError as PlaywrightTimeoutError,
    sync_playwright,
)
from rich.progress import track
from tenacity import retry, stop_after_attempt, wait_fixed

from .types import GoogleRating
from .utils.file_ops import load_json, save_json
from .utils.logger import console
from .utils.validators import validate_file_exists


def extract_unique_hotels(packages: list[dict]) -> list[str]:
    """Extract unique hotel names from packages.

    Args:
        packages: List of package dictionaries

    Returns:
        List of unique hotel names
    """
    hotels = {pkg.get("hotel_name") for pkg in packages if pkg.get("hotel_name")}
    return sorted(hotels)


def scrape_hotel(hotel_name: str, page: Page, debug: bool = False) -> GoogleRating:
    """Scrape Google Maps for a single hotel.

    Args:
        hotel_name: Name of the hotel
        page: Playwright page instance

    Returns:
        GoogleRating object with scraped data
    """
    search_url = f"https://www.google.com/maps/search/{hotel_name.replace(' ', '+')}"

    try:
        # Navigate to Google Maps and wait for results pane to appear
        page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_selector('div[role="main"]', timeout=45000)
        page.wait_for_timeout(2000)  # Let dynamic content load

        # Extract rating (e.g., "4.5 stars")
        rating = None
        try:
            rating_elem = page.locator('span[role="img"][aria-label*="stars"]').first
            rating_text = rating_elem.get_attribute("aria-label")
            if rating_text:
                rating = float(rating_text.split()[0])
        except Exception:
            pass

        # Extract review count (supports localized text)
        review_count = None
        try:
            reviews_elem = page.locator(
                'div[role="main"] span[role="img"][aria-label*="review"], '
                'div[role="main"] span[role="img"][aria-label*="reseñ"]'
            ).first
            reviews_text = reviews_elem.get_attribute("aria-label") or reviews_elem.text_content()
            if reviews_text:
                digits = "".join(ch for ch in reviews_text if ch.isdigit())
                if digits:
                    review_count = int(digits)
            if debug:
                console.print(
                    f"[yellow]Debug[/yellow] reviews source for {hotel_name}: '{reviews_text}' -> {review_count}"
                )
        except Exception:
            pass

        return GoogleRating(
            hotel_name=hotel_name,
            rating=rating,
            review_count=review_count,
        )

    except PlaywrightTimeoutError:
        console.print(f"[yellow]⚠[/yellow] Timeout scraping {hotel_name}")
        return GoogleRating(hotel_name=hotel_name)
    except Exception as e:
        console.print(f"[red]✗[/red] Error scraping {hotel_name}: {e}")
        return GoogleRating(hotel_name=hotel_name)


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def scrape_with_retry(hotel_name: str, page: Page, debug: bool = False) -> GoogleRating:
    """Scrape hotel with retry logic."""
    return scrape_hotel(hotel_name, page, debug=debug)


@click.command()
@click.option("--destination", required=True, type=str, help="Destination name")
@click.option("--source", required=True, type=str, help="Package source")
@click.option("--headless", default=True, type=bool, help="Run browser in headless mode")
@click.option(
    "--debug",
    is_flag=True,
    default=False,
    help="Capture Playwright traces and screenshots for debugging",
)
def main(destination: str, source: str, headless: bool, debug: bool) -> None:
    """Scrape Google Maps ratings for hotels."""
    # Find most recent filtered file
    filtered_dir = Path(f"data/{destination}/{source}/filtered")
    output_path = Path(f"data/{destination}/{source}/scraped/google_ratings.json")

    try:
        if not filtered_dir.exists() or not list(filtered_dir.glob("*.json")):
            raise FileNotFoundError(f"No filtered packages found in {filtered_dir}")

        filtered_file = max(filtered_dir.glob("*.json"), key=lambda p: p.stat().st_mtime)
        console.print(f"[blue]Loading filtered packages from:[/blue] {filtered_file}")

        # Load and extract hotels
        packages = load_json(filtered_file)
        hotels = extract_unique_hotels(packages)

        console.print(f"[blue]Found {len(hotels)} unique hotels to scrape[/blue]")

        scrape_dir = Path(f"data/{destination}/{source}/scraped")
        scrape_dir.mkdir(parents=True, exist_ok=True)
        debug_dir = scrape_dir / "debug"
        if debug:
            debug_dir.mkdir(parents=True, exist_ok=True)

        # Scrape with Playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            page = browser.new_page()

            trace_path = None
            if debug:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                trace_path = debug_dir / f"trace_{timestamp}.zip"
                page.context.tracing.start(
                    screenshots=True,
                    snapshots=True,
                    sources=True,
                )

            ratings = []
            for hotel in track(hotels, description="Scraping hotels"):
                try:
                    rating = scrape_with_retry(hotel, page, debug=debug)
                    ratings.append(rating.model_dump())
                except Exception as e:
                    console.print(f"[red]Failed to scrape {hotel}:[/red] {e}")
                    ratings.append(GoogleRating(hotel_name=hotel).model_dump())
                    if debug:
                        screenshot_path = debug_dir / f"{hotel.replace(' ', '_')}.png"
                        page.screenshot(path=str(screenshot_path), full_page=True)
                        console.print(
                            f"[yellow]Captured screenshot for {hotel} at {screenshot_path}[/yellow]"
                        )

            if debug and trace_path:
                page.context.tracing.stop(path=str(trace_path))
                console.print(
                    f"[blue]Playwright trace saved to:[/blue] {trace_path}\n"
                    "Inspect with `playwright show-trace path/to/trace.zip`."
                )

            browser.close()

        # Save results
        save_json(ratings, output_path)

        # Report
        success_count = sum(1 for r in ratings if r.get("rating") is not None)
        console.print(f"[green]✓[/green] Scraped {success_count}/{len(hotels)} hotels successfully")
        console.print(f"[blue]Output:[/blue] {output_path}")

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


if __name__ == "__main__":
    main()
