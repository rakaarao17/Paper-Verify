"""Reporter to format verification results."""

from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from .validator import VerificationResult, MatchStatus


class Reporter:
    """Format and output verification results."""
    
    STATUS_STYLES = {
        MatchStatus.EXACT_MATCH: ("✅", "green"),
        MatchStatus.CLOSE_MATCH: ("⚠️", "yellow"),
        MatchStatus.MISMATCH: ("❌", "red"),
        MatchStatus.UNVERIFIED: ("❓", "dim"),
    }
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
    
    def print_results(self, results: List[VerificationResult]):
        """Print results to terminal with colors."""
        
        # Summary statistics
        stats = self._calculate_stats(results)
        
        # Header
        self.console.print()
        self.console.print(Panel.fit(
            "[bold]PAPER-VERIFY REPORT[/bold]",
            border_style="blue",
        ))
        self.console.print()
        
        # Results table
        table = Table(box=box.ROUNDED, show_header=True)
        table.add_column("Status", width=3)
        table.add_column("Line", justify="right", width=5)
        table.add_column("Claim", width=15)
        table.add_column("Context", width=30)
        table.add_column("Result", width=35)
        
        for result in results:
            # Skip unverified for cleaner output
            if result.status == MatchStatus.UNVERIFIED:
                continue
            
            icon, style = self.STATUS_STYLES[result.status]
            
            claim_str = f"{result.claim.value}"
            context = result.claim.context[:30].strip()
            
            if result.matched_value:
                source = Path(result.matched_value.source_file).stem
                result_str = f"{result.matched_value.value} ({source})"
            else:
                result_str = "-"
            
            table.add_row(
                icon,
                str(result.claim.line_number),
                f"[{style}]{claim_str}[/]",
                context,
                result_str,
            )
        
        self.console.print(table)
        
        # Summary
        self.console.print()
        self._print_summary(stats)
    
    def generate_markdown(self, results: List[VerificationResult]) -> str:
        """Generate a markdown report."""
        stats = self._calculate_stats(results)
        
        lines = [
            "# Paper Verification Report",
            "",
            "## Summary",
            "",
            f"- **Total claims checked**: {stats['total']}",
            f"- **Exact matches**: {stats['exact']} ✅",
            f"- **Close matches**: {stats['close']} ⚠️",
            f"- **Mismatches**: {stats['mismatch']} ❌",
            f"- **Unverified**: {stats['unverified']}",
            "",
            "## Details",
            "",
            "| Line | Claim | Status | Matched Value | Source |",
            "|------|-------|--------|---------------|--------|",
        ]
        
        for result in results:
            if result.status == MatchStatus.UNVERIFIED:
                continue
            
            icon, _ = self.STATUS_STYLES[result.status]
            
            if result.matched_value:
                source = Path(result.matched_value.source_file).stem
                matched = f"{result.matched_value.value}"
            else:
                source = "-"
                matched = "-"
            
            lines.append(
                f"| {result.claim.line_number} | {result.claim.value} | "
                f"{icon} | {matched} | {source} |"
            )
        
        return "\n".join(lines)
    
    def save_report(self, results: List[VerificationResult], filepath: Path):
        """Save markdown report to file."""
        content = self.generate_markdown(results)
        filepath = Path(filepath)
        filepath.write_text(content, encoding='utf-8')
    
    def _calculate_stats(self, results: List[VerificationResult]) -> dict:
        """Calculate summary statistics."""
        stats = {
            'total': len(results),
            'exact': 0,
            'close': 0,
            'mismatch': 0,
            'unverified': 0,
        }
        
        for r in results:
            if r.status == MatchStatus.EXACT_MATCH:
                stats['exact'] += 1
            elif r.status == MatchStatus.CLOSE_MATCH:
                stats['close'] += 1
            elif r.status == MatchStatus.MISMATCH:
                stats['mismatch'] += 1
            else:
                stats['unverified'] += 1
        
        return stats
    
    def _print_summary(self, stats: dict):
        """Print summary panel."""
        if stats['mismatch'] == 0:
            style = "green"
            msg = "All verified claims match! ✅"
        elif stats['mismatch'] <= 2:
            style = "yellow"
            msg = f"Found {stats['mismatch']} potential mismatch(es) ⚠️"
        else:
            style = "red"
            msg = f"Found {stats['mismatch']} mismatches! ❌"
        
        self.console.print(Panel(
            f"[bold]{msg}[/bold]\n\n"
            f"Checked: {stats['total']} | "
            f"Exact: {stats['exact']} | "
            f"Close: {stats['close']} | "
            f"Mismatch: {stats['mismatch']}",
            border_style=style,
        ))
