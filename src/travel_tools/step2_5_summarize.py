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
    model_name: str = "gemini-1.5-flash",
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

    # Combine all review texts
    reviews_text = "\n\n---\n\n".join(
        [
            f"Rating: {r['rating']}/5\nDate: {r['date']}\nReviewer: {r.get('reviewer_name', 'Anonymous')}\n\n{r['text']}"
            for r in reviews
        ]
    )

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
            max_output_tokens=2048,
        ),
    )

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


def process_hotel_ratings(
    ratings_file: Path,
    output_file: Path,
    model_name: str = "gemini-1.5-flash",
    rate_limit_delay: float = 1.0,
    test_single: bool = False,
) -> None:
    """Process hotel ratings and generate AI summaries.

    Args:
        ratings_file: Path to scraped ratings JSON file
        output_file: Path to save summarized ratings
        model_name: Gemini model to use
        rate_limit_delay: Delay between API calls (seconds)
        test_single: Only process first hotel (for testing)
    """
    # Load scraped ratings
    ratings_data: list[GoogleRating] = [
        GoogleRating(**r) for r in load_json(ratings_file)
    ]

    console.print(f"[blue]Loaded {len(ratings_data)} hotel ratings[/blue]")

    if test_single:
        ratings_data = ratings_data[:1]
        console.print("[yellow]Test mode: Only processing first hotel[/yellow]")

    # Process each hotel
    summarized_ratings = []

    for rating in track(
        ratings_data,
        description="Summarizing reviews",
        console=console,
    ):
        try:
            if not rating.reviews:
                console.print(
                    f"[yellow]⚠ {rating.hotel_name}: No reviews to summarize[/yellow]"
                )
                # Keep the rating without summary
                summarized_ratings.append(rating.model_dump())
                continue

            console.print(f"\n[cyan]Processing {rating.hotel_name}...[/cyan]")
            console.print(f"  Reviews to analyze: {len(rating.reviews)}")

            # Generate summary
            summary = summarize_reviews_with_gemini(
                hotel_name=rating.hotel_name,
                reviews=[r.model_dump() for r in rating.reviews],
                model_name=model_name,
            )

            console.print(f"  [green]✓ Summary generated[/green]")
            console.print(f"    Good points: {len(summary.good_points)}")
            console.print(f"    Bad points: {len(summary.bad_points)}")
            console.print(f"    Ugly points: {len(summary.ugly_points)}")

            # Add summary to rating (create new dict to avoid mutating original)
            rating_dict = rating.model_dump()
            rating_dict["review_summary"] = summary.model_dump()
            summarized_ratings.append(rating_dict)

            # Rate limiting
            if rate_limit_delay > 0:
                time.sleep(rate_limit_delay)

        except Exception as e:
            console.print(f"[red]✗ Error summarizing {rating.hotel_name}: {e}[/red]")
            # Keep the rating without summary
            summarized_ratings.append(rating.model_dump())
            continue

    # Save results
    output_file.parent.mkdir(parents=True, exist_ok=True)
    save_json(output_file, summarized_ratings)

    console.print(f"\n[green]✓ Saved summarized ratings to:[/green] {output_file}")
    console.print(f"[blue]Processed {len(summarized_ratings)} hotels[/blue]")


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
    default="gemini-1.5-flash",
    help="Gemini model to use (default: gemini-1.5-flash)",
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
def main(
    destination: str,
    source: str,
    api_key: str | None,
    model: str,
    rate_limit: float,
    test_single_hotel: bool,
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
    ratings_file = Path(f"data/{destination}/{source}/scraped/ratings.json")
    output_file = Path(f"data/{destination}/{source}/scraped/ratings_with_summaries.json")

    if not ratings_file.exists():
        console.print(f"[red]Error: Ratings file not found: {ratings_file}[/red]")
        raise click.Abort()

    console.print(f"[blue]Input:[/blue] {ratings_file}")
    console.print(f"[blue]Output:[/blue] {output_file}")
    console.print(f"[blue]Model:[/blue] {model}")
    console.print(f"[blue]Rate limit:[/blue] {rate_limit}s between calls\n")

    # Process ratings
    process_hotel_ratings(
        ratings_file=ratings_file,
        output_file=output_file,
        model_name=model,
        rate_limit_delay=rate_limit,
        test_single=test_single_hotel,
    )


if __name__ == "__main__":
    main()
