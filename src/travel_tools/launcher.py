"""Pipeline launcher with interactive and batch modes."""

import json
import os
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

console = Console()


def run_cmd(cmd: str, step: str) -> None:
    console.print(f"[blue]Running:[/blue] {cmd}")
    result = os.system(cmd)
    if result != 0:
        raise RuntimeError(f"{step} failed with exit code {result}")


def load_destinations() -> dict:
    config_path = Path("config/destinations.json")
    if not config_path.exists():
        raise FileNotFoundError(f"Missing destinations config: {config_path}")
    return json.loads(config_path.read_text())


def run_pipeline(
    destination: str,
    source: str,
    budget: float,
    hotel: str | None,
    force_scrape: bool,
    force_summarize: bool,
    api_key: str | None,
) -> None:
    console.print(
        Panel.fit(
            f"🌴 Pipeline: {destination} / {source}"
            + (f" / hotel: {hotel}" if hotel else ""),
            style="bold blue",
        )
    )
    run_cmd(
        f"python -m travel_tools.step1_filter --destination {destination} --source {source} --budget {budget}",
        "Filter",
    )

    scrape_cmd = (
        f"python -m travel_tools.step2_scrape --destination {destination} --source {source}"
    )
    if hotel:
        scrape_cmd += f' --hotel "{hotel}"'
    if force_scrape:
        scrape_cmd += " --force-scrape"
    run_cmd(scrape_cmd, "Scrape")

    if api_key:
        summarize_cmd = (
            f"python -m travel_tools.step2_5_summarize --destination {destination} --source {source} "
            f'--api-key "{api_key}" --rate-limit 1.0'
        )
        if hotel:
            summarize_cmd += f' --hotel "{hotel}"'
        if force_summarize:
            summarize_cmd += " --force-summarize"
        run_cmd(summarize_cmd, "Summarize")
    else:
        console.print(
            "[yellow]Skipping summarization (no GEMINI_API_KEY provided).[/yellow]"
        )

    merge_cmd = (
        f"python -m travel_tools.step3_merge --destination {destination} --source {source}"
    )
    if hotel:
        merge_cmd += f' --hotel "{hotel}"'
    run_cmd(merge_cmd, "Merge")

    normalize_cmd = (
        f"python -m travel_tools.step3_5_normalize --destination {destination} --source {source}"
    )
    run_cmd(normalize_cmd, "Normalize")

    web_cmd = (
        f"python -m travel_tools.step4_generate_web --destination {destination} --source {source}"
    )
    run_cmd(web_cmd, "Generate web JSON")

    console.print(
        f"[green]✓ Completed pipeline for {destination}/{source}[/green]\n"
    )


def run_all(
    budget: float,
    hotel: str | None,
    force_scrape: bool,
    force_summarize: bool,
    api_key: str | None,
) -> None:
    destinations = load_destinations()
    for dest, meta in destinations.items():
        sources = meta.get("sources", [])
        for source in sources:
            try:
                run_pipeline(
                    destination=dest,
                    source=source,
                    budget=budget,
                    hotel=hotel,
                    force_scrape=force_scrape,
                    force_summarize=force_summarize,
                    api_key=api_key,
                )
            except Exception as exc:
                console.print(
                    f"[red]Pipeline failed for {dest}/{source}: {exc}[/red]"
                )
                raise


@click.command()
@click.option("--destination", type=str, help="Destination slug")
@click.option("--source", type=str, help="Source slug")
@click.option("--budget", type=float, default=None, help="Budget (CAD)")
@click.option("--all", "run_all_flag", is_flag=True, help="Process all destinations/sources")
@click.option("--hotel", type=str, default=None, help="Only process this hotel name")
@click.option(
    "--force-scrape",
    is_flag=True,
    default=False,
    help="Force re-scraping even if data exists",
)
@click.option(
    "--force-summarize",
    is_flag=True,
    default=False,
    help="Force re-summarization even if summaries exist",
)
@click.option(
    "--api-key",
    type=str,
    default=None,
    help="Gemini API key; defaults to GEMINI_API_KEY env var",
)
def main(
    destination: str | None,
    source: str | None,
    budget: float | None,
    run_all_flag: bool,
    hotel: str | None,
    force_scrape: bool,
    force_summarize: bool,
    api_key: str | None,
) -> None:
    """Run the pipeline interactively or in batch."""
    api_key = api_key or os.getenv("GEMINI_API_KEY")
    budget = budget or 5000

    if run_all_flag:
        run_all(
            budget=budget,
            hotel=hotel,
            force_scrape=force_scrape,
            force_summarize=force_summarize,
            api_key=api_key,
        )
        return

    if destination and source:
        run_pipeline(
            destination=destination,
            source=source,
            budget=budget,
            hotel=hotel,
            force_scrape=force_scrape,
            force_summarize=force_summarize,
            api_key=api_key,
        )
        return

    # Interactive fallback
    console.print(Panel.fit("🌴 Travel Tools Pipeline", style="bold blue"))

    destination = destination or Prompt.ask(
        "Destination",
        choices=["cancun", "punta-cana", "riviera-maya"],
        default="cancun",
    )
    source = source or Prompt.ask(
        "Package source", choices=["transat", "expedia", "sunwing"], default="transat"
    )
    budget_str = str(budget or Prompt.ask("Budget (CAD)", default="5000"))
    try:
        budget_val = float(budget_str)
    except ValueError:
        console.print("[red]Error:[/red] Invalid budget amount")
        sys.exit(1)
    budget = budget_val

    raw_data_path = Path(f"data/{destination}/{source}/raw/packages.json")
    if not raw_data_path.exists():
        console.print(
            f"\n[yellow]Warning:[/yellow] Raw data not found at {raw_data_path}"
        )
        console.print("[yellow]Please add packages.json to the raw/ directory first.[/yellow]")
        sys.exit(1)

    if not Confirm.ask("\nProceed with pipeline?"):
        console.print("[yellow]Pipeline cancelled.[/yellow]")
        return

    run_pipeline(
        destination=destination,
        source=source,
        budget=budget,
        hotel=hotel,
        force_scrape=force_scrape,
        force_summarize=force_summarize,
        api_key=api_key,
    )


if __name__ == "__main__":
    main()
