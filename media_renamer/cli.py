import logging
from pathlib import Path
from typing import List, Optional

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from media_renamer.config import Config
from media_renamer.models import RenameResult
from media_renamer.renamer import FileRenamer


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


@click.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option("--dry-run", is_flag=True, help="Preview changes without renaming files")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--tmdb-key", help="TMDB API key (overrides env var)")
@click.option("--tvdb-key", help="TVDB API key (overrides env var)")
@click.option(
    "--movie-pattern", help='Movie filename pattern (default: "{title} ({year})")'
)
@click.option(
    "--tv-pattern",
    help='TV show filename pattern (default: "{title} - S{season:02d}E{episode:02d} - {episode_title}")',
)
@click.option("--extensions", help="Comma-separated list of file extensions to process")
def main(
    path: Path,
    dry_run: bool,
    verbose: bool,
    tmdb_key: Optional[str],
    tvdb_key: Optional[str],
    movie_pattern: Optional[str],
    tv_pattern: Optional[str],
    extensions: Optional[str],
) -> None:
    """
    Rename movie and TV show files using metadata from TVDB and TMDB.

    PATH: Directory containing media files to rename
    """
    load_dotenv()
    setup_logging(verbose)

    console = Console()

    config = Config.load_from_env()

    if dry_run:
        config.dry_run = True
    if verbose:
        config.verbose = True
    if tmdb_key:
        config.tmdb_api_key = tmdb_key
    if tvdb_key:
        config.tvdb_api_key = tvdb_key
    if movie_pattern:
        config.movie_pattern = movie_pattern
    if tv_pattern:
        config.tv_pattern = tv_pattern
    if extensions:
        config.supported_extensions = [ext.strip() for ext in extensions.split(",")]

    if not config.tmdb_api_key and not config.tvdb_api_key:
        console.print(
            "[yellow]Warning: No API keys provided. Limited metadata will be available.[/yellow]"
        )

    renamer = FileRenamer(config)

    console.print(f"[blue]Processing directory: {path}[/blue]")
    console.print(f"[blue]Dry run: {config.dry_run}[/blue]")
    console.print(
        f"[blue]Supported extensions: {', '.join(config.supported_extensions)}[/blue]"
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Processing files...", total=None)
        results = renamer.process_directory(path)
        progress.update(task, completed=100)

    if results:
        display_results(console, results, config.dry_run)
    else:
        console.print("[yellow]No media files found to process.[/yellow]")


def display_results(
    console: Console, results: List[RenameResult], dry_run: bool
) -> None:
    """Display rename results in a formatted table"""

    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Status", style="dim", width=8)
    table.add_column("Original", style="cyan")
    table.add_column("New", style="green")
    table.add_column("Error", style="red")

    for result in results:
        status = "✓" if result.success else "✗"
        original = str(result.original_path.name)
        new = str(result.new_path.name) if result.success else ""
        error = result.error or ""

        table.add_row(status, original, new, error)

    console.print(table)

    action = "Would rename" if dry_run else "Renamed"
    console.print(f"\n[green]{action} {len(successful)} files successfully[/green]")

    if failed:
        console.print(f"[red]Failed to rename {len(failed)} files[/red]")


if __name__ == "__main__":
    main()
