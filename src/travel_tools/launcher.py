"""Interactive pipeline launcher."""

import os
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

console = Console()


@click.command()
def main() -> None:
    """Interactive travel tools pipeline launcher."""
    console.print(Panel.fit("🌴 Travel Tools Pipeline", style="bold blue"))

    # Get inputs
    console.print("\n[bold]Configuration:[/bold]")

    destination = Prompt.ask(
        "Destination",
        choices=["cancun", "punta-cana", "riviera-maya"],
        default="cancun",
    )

    source = Prompt.ask(
        "Package source", choices=["transat", "expedia", "sunwing"], default="transat"
    )

    budget_str = Prompt.ask("Budget (CAD)", default="5000")
    try:
        budget = float(budget_str)
    except ValueError:
        console.print("[red]Error:[/red] Invalid budget amount")
        sys.exit(1)

    # Show configuration
    console.print(f"\n[blue]Pipeline Configuration:[/blue]")
    console.print(f"  Destination: {destination}")
    console.print(f"  Source: {source}")
    console.print(f"  Budget: ${budget:,.0f}")
    console.print(f"  Data path: data/{destination}/{source}/")

    # Check if raw data exists
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

    # Step 1: Filter
    console.print("\n" + "=" * 60)
    console.print("[bold cyan]Step 1: Filter packages by budget[/bold cyan]")
    console.print("=" * 60)

    cmd = f"python -m travel_tools.step1_filter --destination {destination} --source {source} --budget {budget}"
    result = os.system(cmd)

    if result != 0:
        console.print("[red]Step 1 failed. Aborting pipeline.[/red]")
        sys.exit(1)

    if not Confirm.ask("\n[bold]Continue to Step 2?[/bold]"):
        console.print("[yellow]Pipeline stopped after Step 1.[/yellow]")
        return

    # Step 2: Scrape
    console.print("\n" + "=" * 60)
    console.print("[bold cyan]Step 2: Scrape hotel ratings from Google Maps[/bold cyan]")
    console.print("=" * 60)
    console.print("[yellow]Note:[/yellow] This may take several minutes...")

    cmd = f"python -m travel_tools.step2_scrape --destination {destination} --source {source}"
    result = os.system(cmd)

    if result != 0:
        console.print("[red]Step 2 failed. Aborting pipeline.[/red]")
        sys.exit(1)

    if not Confirm.ask("\n[bold]Continue to Step 3?[/bold]"):
        console.print("[yellow]Pipeline stopped after Step 2.[/yellow]")
        return

    # Step 3: Merge
    console.print("\n" + "=" * 60)
    console.print("[bold cyan]Step 3: Merge package data with ratings[/bold cyan]")
    console.print("=" * 60)

    cmd = f"python -m travel_tools.step3_merge --destination {destination} --source {source}"
    result = os.system(cmd)

    if result != 0:
        console.print("[red]Step 3 failed. Aborting pipeline.[/red]")
        sys.exit(1)

    if not Confirm.ask("\n[bold]Continue to Step 4?[/bold]"):
        console.print("[yellow]Pipeline stopped after Step 3.[/yellow]")
        return

    # Step 4: Generate hotels.json for the viewer
    console.print("\n" + "=" * 60)
    console.print("[bold cyan]Step 4: Generate hotels.json for the viewer[/bold cyan]")
    console.print("=" * 60)

    cmd = f"python -m travel_tools.step4_generate_web --destination {destination} --source {source}"
    result = os.system(cmd)

    if result != 0:
        console.print("[red]Step 4 failed. Aborting pipeline.[/red]")
        sys.exit(1)

    # Success!
    console.print("\n" + "=" * 60)
    console.print("[green bold]✓ Pipeline completed successfully![/green bold]")
    console.print("=" * 60)

    data_path = Path(f"outputs/{destination}/{source}/hotels.json")
    console.print(f"\n[blue]View your results:[/blue]")
    console.print(f"  Data file: {data_path.absolute()}")
    console.print("\n[blue]Next steps:[/blue]")
    console.print("  1. cd web_client && npm install && npm run build")
    console.print("  2. cd ../outputs && python -m http.server 8000")
    console.print("  3. Visit http://localhost:8000/viewer/ and pick your destination/source")


if __name__ == "__main__":
    main()
