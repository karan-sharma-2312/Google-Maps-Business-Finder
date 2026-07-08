"""Typer-based command line interface for the platform.

The CLI is the first operational entry point for local development workflows.
It shares the same settings and logging stack as the API and workers.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from app.config.settings import Settings, get_settings
from app.core.logging import configure_logging, get_logger
from app.services import GoogleMapsDiscoveryService, SeoAnalyzerService, WebsiteAnalyzerService

app = typer.Typer(
    name="bia",
    help="Business Intelligence AI Agent command line interface.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()


def _serialize_settings(settings: Settings) -> dict[str, object]:
    """Convert settings model to a JSON-serializable dictionary.

    Secret values remain masked by Pydantic's serializer.
    """
    return settings.model_dump(mode="json")


@app.command("version")
def version() -> None:
    """Print application name, version, and runtime environment."""
    settings = get_settings()

    table = Table(title="Application Info", show_header=True, header_style="bold cyan")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Name", settings.app.name)
    table.add_row("Version", settings.app.version)
    table.add_row("Environment", settings.app.environment.value)
    table.add_row("Debug", str(settings.app.debug))

    console.print(table)


@app.command("show-config")
def show_config(pretty: bool = typer.Option(True, "--pretty/--compact", help="Pretty-print JSON output.")) -> None:
    """Render the currently loaded runtime configuration as JSON."""
    settings = get_settings()
    payload = _serialize_settings(settings)

    if pretty:
        console.print_json(data=payload)
        return

    console.print(json.dumps(payload, separators=(",", ":"), ensure_ascii=True))


@app.command("init-dirs")
def init_dirs() -> None:
    """Create required runtime directories for local execution."""
    settings = get_settings()
    logger = get_logger({"command": "init-dirs"})

    directories: list[Path] = [
        settings.paths.data_dir,
        settings.paths.log_dir,
        settings.paths.export_dir,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info("Ensured directory exists: {}", directory)

    console.print("Runtime directories are ready.")


@app.command("google-maps-discover")
def google_maps_discover(
    query: str = typer.Option(..., "--query", "-q", help="Business search query."),
    location: str | None = typer.Option(None, "--location", "-l", help="Optional location constraint."),
    max_results: int | None = typer.Option(
        None,
        "--max-results",
        "-m",
        min=1,
        max=200,
        help="Maximum number of businesses to discover.",
    ),
    save_json: bool = typer.Option(True, "--save-json/--no-save-json", help="Persist discovery output to JSON."),
) -> None:
    """Run Google Maps business discovery workflow from the CLI."""
    settings = get_settings()
    logger = get_logger({"command": "google-maps-discover"})
    service = GoogleMapsDiscoveryService(settings)

    effective_max_results = max_results or settings.scraper.google_maps_default_max_results
    try:
        result = asyncio.run(service.discover(query=query, location=location, max_results=effective_max_results))
    except Exception as exc:  # noqa: BLE001
        logger.exception("Google Maps discovery failed: {}", exc)
        raise typer.Exit(code=1) from exc

    table = Table(title="Google Maps Discovery", show_header=True, header_style="bold green")
    table.add_column("Query")
    table.add_column("Location")
    table.add_column("Requested")
    table.add_column("Discovered")
    table.add_row(query, location or "-", str(effective_max_results), str(result.discovered_count))
    console.print(table)

    if result.businesses:
        preview = Table(title="Top Results", show_header=True, header_style="bold cyan")
        preview.add_column("#")
        preview.add_column("Name")
        preview.add_column("Category")
        preview.add_column("Rating")
        preview.add_column("Reviews")

        for index, business in enumerate(result.businesses[:10], start=1):
            preview.add_row(
                str(index),
                business.business_name,
                business.category or "-",
                str(business.rating) if business.rating is not None else "-",
                str(business.reviews_count) if business.reviews_count is not None else "-",
            )

        console.print(preview)

    if save_json:
        timestamp = result.businesses[0].discovered_at.strftime("%Y%m%d_%H%M%S") if result.businesses else "run"
        file_name = f"google_maps_{query.replace(' ', '_').lower()}_{timestamp}.json"
        output_path = settings.paths.export_dir / file_name
        saved = service.save_json_report(result, output_path)
        console.print(f"Saved report: {saved}")
        logger.info("Google Maps discovery report saved at {}", saved)


@app.command("website-analyze")
def website_analyze(
    url: str = typer.Option(..., "--url", "-u", help="Website URL to analyze."),
    save_json: bool = typer.Option(True, "--save-json/--no-save-json", help="Persist analysis output to JSON."),
) -> None:
    """Analyze a website and extract contact/social/technology signals."""
    settings = get_settings()
    logger = get_logger({"command": "website-analyze"})
    service = WebsiteAnalyzerService(settings)

    try:
        result = service.analyze(url)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Website analysis failed for {}: {}", url, exc)
        raise typer.Exit(code=1) from exc

    table = Table(title="Website Analysis", show_header=True, header_style="bold magenta")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_row("Final URL", str(result.final_url))
    table.add_row("Title", result.title or "-")
    table.add_row("Emails", str(len(result.emails)))
    table.add_row("Phone Numbers", str(len(result.phone_numbers)))
    table.add_row("Facebook Links", str(len(result.social_links.facebook)))
    table.add_row("Instagram Links", str(len(result.social_links.instagram)))
    table.add_row("LinkedIn Links", str(len(result.social_links.linkedin)))
    table.add_row("Analytics IDs", str(len(result.analytics_ids)))
    table.add_row("Schema Types", str(len(result.schema_types)))
    console.print(table)

    if save_json:
        domain = url.replace("https://", "").replace("http://", "").replace("/", "_").lower()
        output_path = settings.paths.export_dir / f"website_analysis_{domain}.json"
        saved = service.save_json_report(result, output_path)
        console.print(f"Saved report: {saved}")


@app.command("seo-analyze")
def seo_analyze(
    url: str = typer.Option(..., "--url", "-u", help="Website URL for SEO analysis."),
    save_json: bool = typer.Option(True, "--save-json/--no-save-json", help="Persist analysis output to JSON."),
) -> None:
    """Analyze website SEO and return score with improvement suggestions."""
    settings = get_settings()
    logger = get_logger({"command": "seo-analyze"})
    service = SeoAnalyzerService(settings)

    try:
        result = service.analyze(url)
    except Exception as exc:  # noqa: BLE001
        logger.exception("SEO analysis failed for {}: {}", url, exc)
        raise typer.Exit(code=1) from exc

    table = Table(title="SEO Analysis", show_header=True, header_style="bold yellow")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_row("Final URL", str(result.final_url))
    table.add_row("Score", str(result.score))
    table.add_row("Issues", str(len(result.issues)))
    table.add_row("Title", result.title or "-")
    table.add_row("Description", result.description or "-")
    table.add_row("H1 Count", str(len(result.h1)))
    table.add_row("Broken Links", str(len(result.broken_links)))
    console.print(table)

    if result.issues:
        issue_table = Table(title="SEO Issues", show_header=True, header_style="bold red")
        issue_table.add_column("Severity")
        issue_table.add_column("Issue")
        issue_table.add_column("Suggestion")
        for issue in result.issues[:10]:
            issue_table.add_row(issue.severity, issue.message, issue.suggestion)
        console.print(issue_table)

    if save_json:
        domain = url.replace("https://", "").replace("http://", "").replace("/", "_").lower()
        output_path = settings.paths.export_dir / f"seo_analysis_{domain}.json"
        saved = service.save_json_report(result, output_path)
        console.print(f"Saved report: {saved}")


@app.callback()
def main() -> None:
    """Initialize shared runtime dependencies before command execution."""
    configure_logging()


if __name__ == "__main__":
    app()
