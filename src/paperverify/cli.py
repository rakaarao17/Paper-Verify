"""CLI for paper-verify."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from . import __version__
from .parser import parse_latex
from .matcher import load_results
from .validator import verify_paper
from .reporter import Reporter


app = typer.Typer(
    name="paperverify",
    help="Validate academic paper claims against experiment results.",
    add_completion=False,
)
console = Console()


@app.command()
def check(
    paper: Path = typer.Argument(
        ...,
        help="Path to LaTeX paper file (.tex)",
        exists=True,
    ),
    results: Path = typer.Option(
        ...,
        "--results", "-r",
        help="Path to results directory",
        exists=True,
    ),
    tolerance: float = typer.Option(
        1.0,
        "--tolerance", "-t",
        help="Tolerance percentage for close matches",
    ),
    report: Optional[Path] = typer.Option(
        None,
        "--report", "-o",
        help="Save markdown report to file",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet", "-q",
        help="Only show mismatches",
    ),
):
    """Check paper claims against result files."""
    
    console.print(f"[bold blue]Paper-Verify v{__version__}[/bold blue]")
    console.print()
    
    # Parse paper
    console.print(f"📄 Parsing [cyan]{paper}[/cyan]...")
    claims = parse_latex(paper)
    console.print(f"   Found [bold]{len(claims)}[/bold] numeric claims")
    
    # Load results
    console.print(f"📊 Loading results from [cyan]{results}[/cyan]...")
    matcher = load_results(results)
    console.print(f"   Loaded [bold]{len(matcher.values)}[/bold] result values")
    
    # Verify
    console.print(f"🔍 Verifying claims (tolerance: {tolerance}%)...")
    verification_results = verify_paper(claims, matcher, tolerance)
    
    # Report
    reporter = Reporter(console)
    reporter.print_results(verification_results)
    
    # Save report if requested
    if report:
        reporter.save_report(verification_results, report)
        console.print(f"\n📝 Report saved to [cyan]{report}[/cyan]")
    
    # Exit code based on mismatches
    mismatches = sum(1 for r in verification_results if r.status.value == "mismatch")
    if mismatches > 0:
        raise typer.Exit(code=1)


@app.command()
def version():
    """Show version information."""
    console.print(f"paper-verify v{__version__}")


@app.callback()
def main():
    """Paper-Verify: Validate academic paper claims against experiment results."""
    pass


if __name__ == "__main__":
    app()
