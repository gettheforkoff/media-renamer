import logging
from pathlib import Path
from typing import Dict, List, Optional

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
@click.option("--consolidate-tv", is_flag=True, help="Consolidate multiple TV show directories into unified structure")
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
    consolidate_tv: bool,
    tmdb_key: Optional[str],
    tvdb_key: Optional[str],
    movie_pattern: Optional[str],
    tv_pattern: Optional[str],
    extensions: Optional[str],
) -> None:
    """
    Rename movie and TV show files using metadata from TVDB and TMDB.
    
    Use --consolidate-tv to merge multiple directories of the same TV show 
    into a unified structure with proper season organization.

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

    console.print(f"[blue]Processing directory: {path}[/blue]")
    console.print(f"[blue]Dry run: {config.dry_run}[/blue]")
    console.print(
        f"[blue]Supported extensions: {', '.join(config.supported_extensions)}[/blue]"
    )

    if consolidate_tv:
        # TV Show Consolidation Mode
        from media_renamer.tv_show_consolidator import TVShowConsolidator
        
        console.print("[cyan]TV Show Consolidation Mode Enabled[/cyan]")
        consolidator = TVShowConsolidator(config)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Consolidating TV shows...", total=None)
            consolidation_results = consolidator.consolidate_tv_shows(path)
            progress.update(task, completed=100)
        
        if consolidation_results:
            display_consolidation_results(console, consolidation_results, config.dry_run)
        else:
            console.print("[yellow]No TV show directories found to consolidate.[/yellow]")
            
    else:
        # Standard File Renaming Mode
        renamer = FileRenamer(config)
        
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


def display_consolidation_results(console: Console, results: List[Dict], dry_run: bool) -> None:
    """Display TV show consolidation results in a formatted table"""
    from typing import Dict, Any
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("TV Show", style="cyan")
    table.add_column("TVDB ID", style="yellow")
    table.add_column("Unified Directory", style="green")
    table.add_column("Operations", style="blue")
    table.add_column("Status", style="dim")
    
    total_operations = 0
    successful_operations = 0
    
    for result in results:
        show_title = result.get("show_title", "Unknown")
        tvdb_id = result.get("tvdb_id", "N/A")
        unified_dir = result.get("unified_directory", "")
        operations = result.get("operations", [])
        
        # Count successful operations
        successful_ops = sum(1 for op in operations if op.get("success", False))
        total_ops = len(operations)
        total_operations += total_ops
        successful_operations += successful_ops
        
        operations_summary = f"{successful_ops}/{total_ops} successful"
        status = "✓" if successful_ops == total_ops else "⚠"
        
        table.add_row(
            show_title,
            str(tvdb_id) if tvdb_id != "N/A" else tvdb_id,
            unified_dir,
            operations_summary,
            status
        )
        
        # Show detailed operations if verbose
        if console._environ.get("VERBOSE"):
            for op in operations:
                source = op.get("source", "")
                destination = op.get("destination", "")
                season = op.get("season")
                success = op.get("success", False)
                error = op.get("error", "")
                
                detail_status = "  ✓" if success else "  ✗"
                season_info = f" → Season {season}" if season else ""
                error_info = f" ({error})" if error else ""
                
                console.print(f"{detail_status} {source}{season_info}{error_info}")
    
    console.print(table)
    
    action = "Would consolidate" if dry_run else "Consolidated"
    console.print(f"\n[green]{action} {len(results)} TV shows with {successful_operations}/{total_operations} successful operations[/green]")
    
    if successful_operations < total_operations:
        failed_ops = total_operations - successful_operations
        console.print(f"[red]{failed_ops} operations failed[/red]")


if __name__ == "__main__":
    main()
