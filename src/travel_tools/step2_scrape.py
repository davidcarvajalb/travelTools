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

from .types import GoogleRating, Review
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


def deduplicate_reviews(reviews: list[Review]) -> list[Review]:
    """Remove duplicate reviews based on text/rating/name."""
    deduped: list[Review] = []
    seen: set[tuple[str | None, int | None, str | None]] = set()
    for review in reviews:
        key = (review.text, review.rating, review.reviewer_name)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(review)
    return deduped


def scrape_reviews(
    hotel_name: str,
    page: Page,
    max_reviews: int = 10,
    debug: bool = False,
    debug_dir: Path | None = None,
) -> list[Review]:
    """Scrape reviews from Google Maps for a hotel.

    Args:
        hotel_name: Name of the hotel
        page: Playwright page instance
        max_reviews: Maximum number of reviews to scrape
        debug: Enable debug logging
        debug_dir: Directory to save debug artifacts

    Returns:
        List of Review objects
    """
    safe_name = hotel_name.replace(' ', '_').replace('/', '_')

    try:
        if debug:
            console.print(f"\n[cyan]{'='*60}[/cyan]")
            console.print(f"[cyan]Starting review scrape for: {hotel_name}[/cyan]")
            console.print(f"[cyan]{'='*60}[/cyan]")

        # Save initial page state
        if debug and debug_dir:
            initial_html = debug_dir / f"{safe_name}_01_initial.html"
            initial_screenshot = debug_dir / f"{safe_name}_01_initial.png"
            with open(initial_html, 'w') as f:
                f.write(page.content())
            page.screenshot(path=str(initial_screenshot))
            console.print(f"[blue]📸 Saved initial state:[/blue] {initial_screenshot}")

        # Click on Reviews tab/button
        if debug:
            console.print(f"[yellow]Step 1: Looking for Reviews tab...[/yellow]")

        reviews_tab_clicked = False
        review_tab_selectors = [
            'button[aria-label*="Reviews"]',
            'button:has-text("Reviews")',
            'div[role="tab"]:has-text("Reviews")',
            'button[jsaction*="pane.reviewChart.moreReviews"]',
            'a:has-text("Reviews")',
        ]
        for sel in review_tab_selectors:
            try:
                page.click(sel, timeout=5000)
                reviews_tab_clicked = True
                if debug:
                    console.print(f"[green]✓ Clicked Reviews tab ({sel})[/green]")
                break
            except Exception as exc:
                if debug:
                    console.print(f"[yellow]  Selector failed ({sel}): {exc}[/yellow]")

        if not reviews_tab_clicked:
            # Fallback: click the first place result (skip ads) and retry
            try:
                result_link = page.locator('a[href*="/place"][aria-label]').first
                result_label = result_link.get_attribute("aria-label", timeout=2000) or ""
                if debug:
                    console.print(f"[yellow]Attempting fallback place click: {result_label}[/yellow]")
                result_link.click(timeout=5000)
                page.wait_for_timeout(2000)
                for sel in review_tab_selectors:
                    try:
                        page.click(sel, timeout=5000)
                        reviews_tab_clicked = True
                        if debug:
                            console.print(f"[green]✓ Clicked Reviews tab after fallback ({sel})[/green]")
                        break
                    except Exception:
                        continue
            except Exception as exc:
                if debug:
                    console.print(f"[yellow]Fallback place click failed: {exc}[/yellow]")

        if not reviews_tab_clicked:
            if debug:
                console.print(f"[red]✗ Could not find Reviews tab[/red]")
                if debug_dir:
                    fail_html = debug_dir / f"{safe_name}_02_no_reviews_tab.html"
                    with open(fail_html, 'w') as f:
                        f.write(page.content())
                    console.print(f"[blue]📄 Saved HTML for inspection: {fail_html}[/blue]")
            return []

        page.wait_for_timeout(2000)  # Wait for reviews to load

        if debug and debug_dir and reviews_tab_clicked:
            after_click_html = debug_dir / f"{safe_name}_02_after_reviews_click.html"
            after_click_screenshot = debug_dir / f"{safe_name}_02_after_reviews_click.png"
            with open(after_click_html, 'w') as f:
                f.write(page.content())
            page.screenshot(path=str(after_click_screenshot))
            console.print(f"[blue]📸 Saved after Reviews click:[/blue] {after_click_screenshot}")

        # Scroll to load more reviews (infinite scroll)
        if debug:
            console.print(f"[yellow]Step 2: Scrolling to load reviews...[/yellow]")

        reviews_container = None
        try:
            loc = page.locator('div[role="feed"]')
            if loc.count() > 0:
                reviews_container = loc.first
        except Exception:
            reviews_container = None

        scroll_target = reviews_container or page
        scroll_iterations = max((max_reviews // 4) + 8, 12)
        loaded = 0
        for i in range(scroll_iterations):
            try:
                scroll_target.scroll_into_view_if_needed(timeout=2000)
            except Exception:
                pass
            page.mouse.wheel(0, 2000)
            page.wait_for_timeout(700)
            try:
                loaded = len((reviews_container or page).locator("div[data-review-id]").all())
            except Exception:
                loaded = 0
            if debug and (i % 2 == 0):
                console.print(f"[blue]  Scroll {i+1}/{scroll_iterations}... found {loaded} review nodes[/blue]")

        if debug:
            console.print(f"[green]✓ Scrolling attempts complete[/green]")

        # Extract review elements
        if debug:
            console.print(f"[yellow]Step 3: Extracting review elements...[/yellow]")

        review_elements = []
        try:
            if reviews_container is not None:
                review_elements = reviews_container.locator("div[data-review-id]").all()
        except Exception:
            review_elements = []
        if not review_elements:
            review_elements = page.locator("div[data-review-id]").all()

        # If we still don't have enough reviews, keep scrolling to try to hit the target
        min_target = max(max_reviews * 3, max_reviews + 15)
        extra_scrolls = 0
        while len(review_elements) < min_target and extra_scrolls < 20:
            try:
                if reviews_container:
                    reviews_container.scroll_into_view_if_needed(timeout=2000)
                page.mouse.wheel(0, 2200)
                page.wait_for_timeout(700)
                review_elements = (reviews_container or page).locator("div[data-review-id]").all()
                extra_scrolls += 1
                if debug:
                    console.print(
                        f"[blue]  Extra scroll {extra_scrolls}/20, found {len(review_elements)} review nodes[/blue]"
                    )
                if len(review_elements) >= min_target:
                    break
            except Exception:
                break

        if debug:
            console.print(f"[blue]Found {len(review_elements)} review elements[/blue]")

            # Save HTML after scrolling
            if debug_dir:
                after_scroll_html = debug_dir / f"{safe_name}_03_after_scroll.html"
                with open(after_scroll_html, 'w') as f:
                    f.write(page.content())
                console.print(f"[blue]📄 Saved HTML with reviews: {after_scroll_html}[/blue]")

        reviews = []
        target_count = max(max_reviews * 2, max_reviews + 10)  # oversample to offset duplicates
        for idx, review_elem in enumerate(review_elements[:target_count]):
            if debug:
                console.print(f"\n[cyan]Processing review {idx+1}/{min(len(review_elements), max_reviews)}...[/cyan]")

            try:
                # Extract review text
                try:
                    text_elem = review_elem.locator('span.wiI7pd').first
                    text = text_elem.text_content(timeout=3000) or ""
                    if debug:
                        console.print(f"  Text: {text[:50]}..." if len(text) > 50 else f"  Text: {text}")
                except Exception as e:
                    if debug:
                        console.print(f"  [red]✗ Failed to get text: {e}[/red]")
                    text = ""

                # Expand "More" button if present
                try:
                    more_button = review_elem.locator('button.w8nwRe').first
                    if more_button.is_visible(timeout=500):
                        more_button.click()
                        page.wait_for_timeout(300)
                        text = text_elem.text_content() or text
                        if debug:
                            console.print(f"  [green]✓ Expanded 'More' button[/green]")
                except Exception:
                    pass  # No "More" button or already expanded

                # Extract star rating
                try:
                    rating_text = ""
                    try:
                        rating_elem = review_elem.locator(
                            'span[aria-label*="star"], span[role="img"][aria-label*="star"]'
                        ).first
                        rating_text = (
                            rating_elem.get_attribute("aria-label", timeout=1500)
                            or rating_elem.text_content(timeout=1500)
                            or ""
                        )
                    except Exception:
                        # Fallback: numeric text like "5/5" in a span (see debug HTML)
                        rating_elem = review_elem.locator('span:has-text("/")').first
                        rating_text = rating_elem.text_content(timeout=1500) or ""

                    numeric_part = rating_text.split("/")[0].split()[0]
                    rating = int(round(float(numeric_part))) if numeric_part else 3
                    if debug:
                        console.print(f"  Rating: {rating} stars (from '{rating_text}')")
                except Exception as e:
                    if debug:
                        console.print(f"  [yellow]⚠ Failed to get rating (defaulting to 3): {e}[/yellow]")
                    rating = 3

                # Extract date
                try:
                    # Try two possible date selectors
                    date_elem = review_elem.locator('span.DZSIDd, span.xRkPPb').first
                    date_text = date_elem.text_content(timeout=3000) or "Unknown"
                    # Clean up text like "a week ago on Google" → "a week ago"
                    date = date_text.split(" on ")[0] if " on " in date_text else date_text
                    if debug:
                        console.print(f"  Date: {date}")
                except Exception as e:
                    if debug:
                        console.print(f"  [yellow]⚠ Failed to get date: {e}[/yellow]")
                    date = "Unknown"

                # Extract reviewer name
                try:
                    # Try to find reviewer name in the div with class d4r55
                    name_elem = review_elem.locator('div.d4r55').first
                    reviewer_name = name_elem.text_content(timeout=3000) or ""
                    reviewer_name = reviewer_name.strip() if reviewer_name else None
                    if debug:
                        console.print(f"  Reviewer: {reviewer_name}")
                except Exception as e:
                    if debug:
                        console.print(f"  [yellow]⚠ Failed to get reviewer name: {e}[/yellow]")
                    reviewer_name = None

                if not text or len(text) < 5:
                    if debug:
                        console.print(f"  [yellow]⚠ Skipping review with insufficient text[/yellow]")
                    continue

                review = Review(
                    text=text,
                    rating=rating,
                    date=date,
                    reviewer_name=reviewer_name
                )
                reviews.append(review)

                if debug:
                    console.print(f"  [green]✓ Successfully parsed review {idx+1}[/green]")

            except Exception as e:
                if debug:
                    console.print(f"  [red]✗ Failed to parse review: {e}[/red]")
                continue

        if debug:
            console.print(f"\n[cyan]{'='*60}[/cyan]")
            console.print(f"[green]✓ Scraped {len(reviews)}/{len(review_elements[:max_reviews])} reviews for {hotel_name}[/green]")
            console.print(f"[cyan]{'='*60}[/cyan]\n")

        # Deduplicate reviews (Google often renders duplicates when scrolling)
        deduped = deduplicate_reviews(reviews)[:max_reviews]

        # Save final results
        if debug and debug_dir:
            reviews_json = debug_dir / f"{safe_name}_04_reviews.json"
            with open(reviews_json, 'w') as f:
                import json
                json.dump([r.model_dump() for r in deduped], f, indent=2)
            console.print(f"[blue]💾 Saved reviews JSON: {reviews_json}[/blue]")

        return deduped

    except PlaywrightTimeoutError as e:
        if debug:
            console.print(f"[red]✗ Timeout scraping reviews for {hotel_name}: {e}[/red]")
        return []
    except Exception as e:
        if debug:
            console.print(f"[red]✗ Error scraping reviews for {hotel_name}: {e}[/red]")
            import traceback
            console.print(f"[red]{traceback.format_exc()}[/red]")
        return []


def scrape_hotel(hotel_name: str, page: Page, max_reviews: int = 0, debug: bool = False, debug_dir: Path | None = None) -> GoogleRating:
    """Scrape Google Maps for a single hotel.

    Args:
        hotel_name: Name of the hotel
        page: Playwright page instance
        max_reviews: Maximum number of reviews to scrape (0 = skip reviews)
        debug: Enable debug logging
        debug_dir: Directory to save debug artifacts

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

        # Scrape reviews if requested
        reviews = []
        if max_reviews > 0:
            reviews = scrape_reviews(hotel_name, page, max_reviews=max_reviews, debug=debug, debug_dir=debug_dir)
            if debug:
                console.print(f"[blue]Scraped {len(reviews)} reviews for {hotel_name}[/blue]")
            if not reviews:
                console.print(
                    f"[yellow]⚠ No reviews scraped for {hotel_name} (max_reviews={max_reviews}).[/yellow] "
                    "Run with --debug for traces/screenshots."
                )

        return GoogleRating(
            hotel_name=hotel_name,
            rating=rating,
            review_count=review_count,
            reviews=reviews,
        )

    except PlaywrightTimeoutError:
        console.print(f"[yellow]⚠[/yellow] Timeout scraping {hotel_name}")
        return GoogleRating(hotel_name=hotel_name)
    except Exception as e:
        console.print(f"[red]✗[/red] Error scraping {hotel_name}: {e}")
        return GoogleRating(hotel_name=hotel_name)


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def scrape_with_retry(hotel_name: str, page: Page, max_reviews: int = 0, debug: bool = False, debug_dir: Path | None = None) -> GoogleRating:
    """Scrape hotel with retry logic."""
    return scrape_hotel(hotel_name, page, max_reviews=max_reviews, debug=debug, debug_dir=debug_dir)


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
@click.option(
    "--max-reviews",
    default=10,
    type=int,
    help="Maximum number of reviews to scrape per hotel (0 = skip reviews, default: 10)",
)
@click.option(
    "--test-single-hotel",
    is_flag=True,
    default=False,
    help="Only scrape the first hotel (for testing)",
)
def main(destination: str, source: str, headless: bool, debug: bool, max_reviews: int, test_single_hotel: bool) -> None:
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

        # Limit to single hotel for testing if requested
        if test_single_hotel:
            hotels = hotels[:1]
            console.print(f"[yellow]Test mode: Only scraping first hotel[/yellow]")

        console.print(f"[blue]Found {len(hotels)} unique hotels to scrape[/blue]")
        if max_reviews > 0:
            console.print(f"[blue]Will scrape up to {max_reviews} reviews per hotel[/blue]")

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
                    rating = scrape_with_retry(hotel, page, max_reviews=max_reviews, debug=debug, debug_dir=debug_dir if debug else None)
                    ratings.append(rating.model_dump())
                    console.print(
                        f"[blue]· {hotel}[/blue] | rating: {rating.rating or '—'} | "
                        f"reviews scraped: {len(rating.reviews)} | review_count field: {rating.review_count}"
                    )
                except Exception as e:
                    console.print(f"[red]Failed to scrape {hotel}:[/red] {e}")
                    ratings.append(GoogleRating(hotel_name=hotel).model_dump())
                    if debug:
                        screenshot_path = debug_dir / f"{hotel.replace(' ', '_')}_error.png"
                        page.screenshot(path=str(screenshot_path), full_page=True)
                        console.print(
                            f"[yellow]Captured error screenshot for {hotel} at {screenshot_path}[/yellow]"
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
