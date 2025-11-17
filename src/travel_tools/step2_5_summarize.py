"""Step 2.5: AI-powered review summarization using Google Gemini API.

This script takes scraped hotel reviews and generates structured summaries
using the Gemini API. It includes rate limiting and error handling.
"""

import json
import os
import time
from pathlib import Path

import click
import google.generativeai as genai
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import track
from tenacity import retry, stop_after_attempt, wait_exponential

from travel_tools.prompts import get_prompt_template
from travel_tools.types import GoogleRating, ReviewSummary
from travel_tools.utils.file_ops import load_json, save_json

# Load environment variables from .env file
load_dotenv()

console = Console()


class SafetyBlockError(Exception):
    """Raised when Gemini blocks a request (finish_reason == 2)."""


def configure_gemini_api(api_key: str | None = None) -> None:
    """Configure the Gemini API with the provided API key.

    Args:
        api_key: Gemini API key. If None, reads from GEMINI_API_KEY env var.

    Raises:
        ValueError: If API key is not provided or found in environment
    """
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError(
            "Gemini API key not found. Please provide via --api-key flag "
            "or set GEMINI_API_KEY environment variable."
        )

    genai.configure(api_key=key)
    console.print("[green]✓ Gemini API configured[/green]")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)
def summarize_reviews_with_gemini(
    hotel_name: str,
    reviews: list[dict],
    model_name: str = "gemini-2.5-flash",
    prompt_provider: str = "gemini",
) -> ReviewSummary:
    """Summarize hotel reviews using Gemini API.

    Args:
        hotel_name: Name of the hotel
        reviews: List of review dictionaries
        model_name: Gemini model to use
        prompt_provider: Prompt template provider ("gemini" or "claude")

    Returns:
        ReviewSummary object with AI-generated insights

    Raises:
        Exception: If API call fails after retries
    """
    if not reviews:
        return ReviewSummary(
            good_points=[],
            bad_points=[],
            ugly_points=[],
            overall_summary="No reviews available for analysis.",
            review_count_analyzed=0,
        )

    # Combine review texts as a JSON array of raw review bodies
    review_texts = [r["text"] for r in reviews]
    reviews_text = json.dumps(review_texts, ensure_ascii=False)

    # Get the appropriate prompt template
    prompt_template = get_prompt_template(prompt_provider)
    prompt = prompt_template.format_review_summarization(hotel_name, reviews_text)

    # Call Gemini API
    model = genai.GenerativeModel(model_name)

    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            temperature=0.3,  # Lower temperature for more consistent output
            top_p=0.95,
            top_k=40,
            max_output_tokens=4096,  # Extra room to avoid truncated JSON
            response_mime_type="application/json",
        ),
    )

    if not response.candidates:
        raise SafetyBlockError("Gemini returned no candidates (possible safety block).")

    finish_reason = getattr(response.candidates[0], "finish_reason", None)
    # The enum value from the API is 2 when blocked for safety.
    if finish_reason == 2 or getattr(finish_reason, "value", None) == 2:
        raise SafetyBlockError("Gemini blocked the request (finish_reason=2).")

    # Parse JSON response
    response_text = response.text.strip()

    # Remove markdown code blocks if present
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        response_text = "\n".join(lines[1:-1])  # Remove first and last lines
        if response_text.startswith("json"):
            response_text = response_text[4:].strip()  # Remove 'json' prefix

    try:
        summary_data = json.loads(response_text)
    except json.JSONDecodeError as e:
        console.print(f"[yellow]⚠ Failed to parse JSON response: {e}[/yellow]")
        console.print(f"[yellow]Response was: {response_text[:200]}...[/yellow]")
        raise

    # Create ReviewSummary from parsed data
    return ReviewSummary(
        good_points=summary_data.get("good_points", []),
        bad_points=summary_data.get("bad_points", []),
        ugly_points=summary_data.get("ugly_points", []),
        overall_summary=summary_data.get("overall_summary", ""),
        review_count_analyzed=summary_data.get("review_count_analyzed", len(reviews)),
    )


def save_progress(
    ratings_data: list[GoogleRating],
    summarized_map: dict[str, dict],
    output_file: Path,
) -> None:
    """Persist current progress so reruns pick up where they left off."""
    ordered_entries = []
    for rating in ratings_data:
        hotel_key = rating.hotel_name.lower()
        if hotel_key in summarized_map:
            ordered_entries.append(summarized_map[hotel_key])

    output_file.parent.mkdir(parents=True, exist_ok=True)
    save_json(ordered_entries, output_file)


def load_existing_summaries(path: Path) -> dict[str, ReviewSummary]:
    """Load previously generated summaries keyed by hotel name (lowercased)."""
    if not path.exists():
        return {}

    summaries: dict[str, ReviewSummary] = {}
    for entry in load_json(path):
        hotel_name = entry.get("hotel_name", "").lower()
        summary_payload = entry.get("review_summary")
        if not hotel_name or not summary_payload:
            continue
        try:
            summaries[hotel_name] = ReviewSummary(**summary_payload)
        except Exception as exc:
            console.print(
                f"[yellow]⚠ Skipping cached summary for {hotel_name}: {exc}[/yellow]"
            )
    return summaries


def load_existing_output(path: Path) -> dict[str, dict]:
    """Load the current ratings_with_summaries file keyed by hotel name."""
    if not path.exists():
        return {}

    existing: dict[str, dict] = {}
    for entry in load_json(path):
        hotel_name = entry.get("hotel_name", "").lower()
        if not hotel_name:
            continue
        existing[hotel_name] = entry
    return existing


def process_hotel_ratings(
    ratings_file: Path,
    output_file: Path,
    model_name: str = "gemini-2.5-flash",
    rate_limit_delay: float = 1.0,
    test_single: bool = False,
    hotel_filter: str | None = None,
    skip_existing_summaries: bool = False,
    existing_summaries: dict[str, ReviewSummary] | None = None,
    existing_output: dict[str, dict] | None = None,
    max_reviews_per_hotel: int | None = None,
    max_new_summaries: int | None = None,
) -> None:
    """Process hotel ratings and generate AI summaries.

    Args:
        ratings_file: Path to scraped ratings JSON file
        output_file: Path to save summarized ratings
        model_name: Gemini model to use
        rate_limit_delay: Delay between API calls (seconds)
        test_single: Only process first hotel (for testing)
        skip_existing_summaries: Skip API call if review_summary already exists
        existing_summaries: Cached summaries keyed by hotel name (lowercased)
        existing_output: Existing ratings_with_summaries keyed by hotel name
        max_reviews_per_hotel: Cap reviews sent per hotel to reduce token usage
        max_new_summaries: Cap number of new summaries generated this run
    """
    # Load scraped ratings
    ratings_data: list[GoogleRating] = [
        GoogleRating(**r) for r in load_json(ratings_file)
    ]

    console.print(f"[blue]Loaded {len(ratings_data)} hotel ratings[/blue]")

    if hotel_filter:
        ratings_data = [
            r for r in ratings_data if r.hotel_name.lower() == hotel_filter.lower()
        ]
        if not ratings_data:
            console.print(
                f"[red]Error: Hotel '{hotel_filter}' not found in ratings file[/red]"
            )
            raise click.Abort()
        console.print(
            f"[yellow]Filtering to hotel:[/yellow] {ratings_data[0].hotel_name}"
        )

    if test_single:
        ratings_data = ratings_data[:1]
        console.print("[yellow]Test mode: Only processing first hotel[/yellow]")

    # Process each hotel
    summarized_ratings_map: dict[str, dict] = existing_output or {}

    for rating in track(
        ratings_data,
        description="Summarizing reviews",
        console=console,
    ):
        try:
            existing_summary = None
            if skip_existing_summaries and existing_summaries:
                existing_summary = existing_summaries.get(rating.hotel_name.lower())

            if existing_summary:
                console.print(
                    f"[green]✓ Skipping {rating.hotel_name}: existing summary found[/green]"
                )
                rating_dict = rating.model_dump()
                rating_dict["review_summary"] = existing_summary.model_dump()
                summarized_ratings_map[rating.hotel_name.lower()] = rating_dict
                save_progress(
                    ratings_data, summarized_ratings_map, output_file
                )
                continue

            if not rating.reviews:
                console.print(
                    f"[yellow]⚠ {rating.hotel_name}: No reviews to summarize[/yellow]"
                )
                # Keep the rating without summary
                summarized_ratings_map[rating.hotel_name.lower()] = rating.model_dump()
                save_progress(
                    ratings_data, summarized_ratings_map, output_file
                )
                continue

            console.print(f"\n[cyan]Processing {rating.hotel_name}...[/cyan]")
            reviews_to_use = rating.reviews
            if max_reviews_per_hotel is not None:
                reviews_to_use = rating.reviews[:max_reviews_per_hotel]
            console.print(f"  Reviews to analyze: {len(reviews_to_use)}")

            # Generate summary
            summary = summarize_reviews_with_gemini(
                hotel_name=rating.hotel_name,
                reviews=[r.model_dump() for r in reviews_to_use],
                model_name=model_name,
            )

            console.print(f"  [green]✓ Summary generated[/green]")
            console.print(f"    Good points: {len(summary.good_points)}")
            console.print(f"    Bad points: {len(summary.bad_points)}")
            console.print(f"    Ugly points: {len(summary.ugly_points)}")

            # Add summary to rating (create new dict to avoid mutating original)
            rating_dict = rating.model_dump()
            rating_dict["review_summary"] = summary.model_dump()
            summarized_ratings_map[rating.hotel_name.lower()] = rating_dict
            save_progress(
                ratings_data, summarized_ratings_map, output_file
            )

            # Rate limiting
            if rate_limit_delay > 0:
                time.sleep(rate_limit_delay)

            if max_new_summaries is not None:
                max_new_summaries -= 1
                if max_new_summaries <= 0:
                    console.print(
                        "[yellow]Reached max-new-summaries limit; stopping early[/yellow]"
                    )
                    break

        except SafetyBlockError as e:
            console.print(
                f"[red]✗ Safety block on {rating.hotel_name}: {e}. Stopping run.[/red]"
            )
            summarized_ratings_map[rating.hotel_name.lower()] = rating.model_dump()
            save_progress(
                ratings_data, summarized_ratings_map, output_file
            )
            break

        except Exception as e:
            console.print(f"[red]✗ Error summarizing {rating.hotel_name}: {e}[/red]")
            # Keep the rating without summary
            summarized_ratings_map[rating.hotel_name.lower()] = rating.model_dump()
            save_progress(
                ratings_data, summarized_ratings_map, output_file
            )
            continue

    # Save final results (redundant but ensures final state)
    save_progress(ratings_data, summarized_ratings_map, output_file)

    console.print(f"\n[green]✓ Saved summarized ratings to:[/green] {output_file}")
    console.print(f"[blue]Processed {len(summarized_ratings_map)} hotels[/blue]")


@click.command()
@click.option("--destination", required=True, type=str, help="Destination name")
@click.option("--source", required=True, type=str, help="Package source")
@click.option(
    "--api-key",
    type=str,
    default=None,
    help="Gemini API key (or set GEMINI_API_KEY env var)",
)
@click.option(
    "--model",
    type=str,
    default="gemini-2.5-flash",
    help="Gemini model to use (default: gemini-2.5-flash)",
)
@click.option(
    "--rate-limit",
    type=float,
    default=1.0,
    help="Delay between API calls in seconds (default: 1.0)",
)
@click.option(
    "--test-single-hotel",
    is_flag=True,
    default=False,
    help="Only process the first hotel (for testing)",
)
@click.option(
    "--hotel-name",
    type=str,
    default=None,
    help="Only summarize the hotel with this exact name",
)
@click.option(
    "--hotel",
    type=str,
    default=None,
    help="Alias for --hotel-name",
)
@click.option(
    "--force-summarize",
    is_flag=True,
    default=False,
    help="Force regeneration even if a summary already exists",
)
@click.option(
    "--max-reviews-per-hotel",
    type=int,
    default=None,
    help="Cap number of reviews sent per hotel to reduce token usage",
)
@click.option(
    "--max-new-summaries",
    type=int,
    default=None,
    help="Stop after generating this many new summaries (existing ones are still skipped)",
)
def main(
    destination: str,
    source: str,
    api_key: str | None,
    model: str,
    rate_limit: float,
    test_single_hotel: bool,
    hotel_name: str | None,
    hotel: str | None,
    force_summarize: bool,
    max_reviews_per_hotel: int | None,
    max_new_summaries: int | None,
) -> None:
    """Generate AI summaries of hotel reviews using Google Gemini API.

    This script reads scraped hotel reviews and generates structured summaries
    using the Gemini API, including good points, bad points, deal-breakers, and
    an overall assessment.

    Example:
        python -m travel_tools.step2_5_summarize \\
            --destination cancun \\
            --source transat \\
            --api-key YOUR_API_KEY
    """
    console.print("\n[bold blue]Step 2.5: AI Review Summarization[/bold blue]\n")

    # Configure API
    try:
        configure_gemini_api(api_key)
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()

    # File paths
    ratings_file = Path(f"data/{destination}/{source}/scraped/google_ratings.json")
    output_file = Path(f"data/{destination}/{source}/scraped/ratings_with_summaries.json")

    if not ratings_file.exists():
        console.print(f"[red]Error: Ratings file not found: {ratings_file}[/red]")
        raise click.Abort()

    console.print(f"[blue]Input:[/blue] {ratings_file}")
    console.print(f"[blue]Output:[/blue] {output_file}")
    console.print(f"[blue]Model:[/blue] {model}")
    console.print(f"[blue]Rate limit:[/blue] {rate_limit}s between calls\n")

    existing_output = load_existing_output(output_file)
    existing_summaries = {}
    skip_existing_summaries = not force_summarize
    if skip_existing_summaries:
        existing_summaries = load_existing_summaries(output_file)
        console.print(
            f"[blue]Skip existing summaries:[/blue] enabled "
            f"({len(existing_summaries)} cached)"
        )

    # Process ratings
    process_hotel_ratings(
        ratings_file=ratings_file,
        output_file=output_file,
        model_name=model,
        rate_limit_delay=rate_limit,
        test_single=test_single_hotel,
        hotel_filter=hotel_name or hotel,
        skip_existing_summaries=skip_existing_summaries,
        existing_summaries=existing_summaries,
        existing_output=existing_output,
        max_reviews_per_hotel=max_reviews_per_hotel,
        max_new_summaries=max_new_summaries,
    )


if __name__ == "__main__":
    main()
