#!/usr/bin/env python
"""Profile the medical-legal case HTML parsing and source adapter normalization."""

import cProfile
import pstats
import io
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rich.console import Console

console = Console()

# Base directory for this repo
BASE_DIR = Path(__file__).parent.parent


def profile_cli():
    """Profile the CLI entry point."""
    console.print("[bold cyan]Profiling CLI...[/bold cyan]")
    
    profiler = cProfile.Profile()
    profiler.enable()
    
    try:
        from corpus_cases_medilegal_nz.cli import main as cli_main
        console.print("[yellow]CLI imported (full run requires CLI args)[/yellow]")
    except ImportError as e:
        console.print(f"[red]Could not import CLI: {e}[/red]")
    
    profiler.disable()
    
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
    ps.print_stats(30)
    console.print(s.getvalue())
    
    output_path = BASE_DIR / "logs" / "profile_cli.txt"
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(s.getvalue())
    console.print(f"[green]Profile saved to {output_path}[/green]")


def profile_fetcher():
    """Profile the fetcher module."""
    console.print("[bold cyan]Profiling fetcher...[/bold cyan]")
    
    profiler = cProfile.Profile()
    profiler.enable()
    
    try:
        from corpus_cases_medilegal_nz.fetcher import fetch_all
        console.print("[yellow]fetcher imported[/yellow]")
    except ImportError as e:
        console.print(f"[red]Could not import fetcher: {e}[/red]")
    
    profiler.disable()
    
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
    ps.print_stats(30)
    console.print(s.getvalue())
    
    output_path = BASE_DIR / "logs" / "profile_fetcher.txt"
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(s.getvalue())
    console.print(f"[green]Profile saved to {output_path}[/green]")


def profile_sources():
    """Profile the source adapters (HTML parsing)."""
    console.print("[bold cyan]Profiling source adapters...[/bold cyan]")
    
    profiler = cProfile.Profile()
    profiler.enable()
    
    try:
        from corpus_cases_medilegal_nz.sources import hdc, hpdt
        console.print("[yellow]source adapters imported[/yellow]")
    except ImportError as e:
        console.print(f"[red]Could not import source adapters: {e}[/red]")
    
    profiler.disable()
    
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
    ps.print_stats(30)
    console.print(s.getvalue())
    
    output_path = BASE_DIR / "logs" / "profile_sources.txt"
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(s.getvalue())
    console.print(f"[green]Profile saved to {output_path}[/green]")


def profile_exporter():
    """Profile the exporter module."""
    console.print("[bold cyan]Profiling exporter...[/bold cyan]")
    
    profiler = cProfile.Profile()
    profiler.enable()
    
    try:
        from corpus_cases_medilegal_nz.exporter import export_to_parquet
        console.print("[yellow]exporter imported[/yellow]")
    except ImportError as e:
        console.print(f"[red]Could not import exporter: {e}[/red]")
    
    profiler.disable()
    
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
    ps.print_stats(30)
    console.print(s.getvalue())
    
    output_path = BASE_DIR / "logs" / "profile_exporter.txt"
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(s.getvalue())
    console.print(f"[green]Profile saved to {output_path}[/green]")


def profile_hf_sync():
    """Profile the HF sync module."""
    console.print("[bold cyan]Profiling HF sync...[/bold cyan]")
    
    profiler = cProfile.Profile()
    profiler.enable()
    
    try:
        from corpus_cases_medilegal_nz.hf_sync import sync_to_hf
        console.print("[yellow]hf_sync imported[/yellow]")
    except ImportError as e:
        console.print(f"[red]Could not import hf_sync: {e}[/red]")
    
    profiler.disable()
    
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
    ps.print_stats(30)
    console.print(s.getvalue())
    
    output_path = BASE_DIR / "logs" / "profile_hf_sync.txt"
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(s.getvalue())
    console.print(f"[green]Profile saved to {output_path}[/green]")


def main():
    """Run all profiling tasks."""
    console.print("[bold]Starting corpus-cases-medilegal-nz profiling[/bold]")
    
    # Ensure logs directory exists
    (BASE_DIR / "logs").mkdir(exist_ok=True)
    
    # Run profiles
    profile_cli()
    profile_fetcher()
    profile_sources()
    profile_exporter()
    profile_hf_sync()
    
    console.print("[bold green]Profiling complete![/bold green]")


if __name__ == "__main__":
    main()
