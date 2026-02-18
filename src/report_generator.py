"""
Report Generator - Formats and outputs quality analysis reports
"""

import json
from datetime import datetime
from typing import Dict, Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn

from .analyzer import QualityReport, QualityScore, RedFlag


class ReportFormatter:
    """Formats quality reports for various outputs"""
    
    def __init__(self):
        self.console = Console()
    
    def print_report(self, report: QualityReport, detailed: bool = True):
        """Print formatted report to console"""
        self.console.print()
        
        # Header
        self._print_header(report)
        
        # Overall Score Panel
        self._print_overall_score(report)
        
        # Executive Summary
        if report.executive_summary:
            self._print_executive_summary(report)
        
        # Category Scores
        self._print_category_scores(report)
        
        # Key Strengths
        self._print_strengths(report)
        
        # Red Flags
        self._print_red_flags(report)
        
        # Investment Thesis
        if report.investment_thesis:
            self._print_investment_thesis(report)
        
        # Risk Assessment
        if report.risk_assessment:
            self._print_risk_assessment(report)
        
        # Detailed Metrics (if requested)
        if detailed:
            self._print_detailed_metrics(report)
        
        self.console.print()
    
    def _print_header(self, report: QualityReport):
        """Print report header"""
        header_text = Text()
        header_text.append("\n" + "═" * 70 + "\n", style="blue")
        header_text.append("  QUALITY MANAGEMENT ANALYSIS REPORT\n", style="bold white")
        header_text.append("═" * 70 + "\n", style="blue")
        header_text.append(f"  Company: ", style="dim")
        header_text.append(f"{report.company_name} ({report.ticker})\n", style="bold cyan")
        header_text.append(f"  Analysis Date: ", style="dim")
        header_text.append(f"{report.analysis_date[:10]}\n", style="white")
        header_text.append(f"  Years Analyzed: ", style="dim")
        header_text.append(f"{report.years_analyzed}\n", style="white")
        header_text.append("═" * 70, style="blue")
        
        self.console.print(header_text)
    
    def _print_overall_score(self, report: QualityReport):
        """Print overall score panel"""
        score = report.overall_score
        
        # Determine color based on score
        if score >= 7:
            color = "green"
            rating = "STRONG"
        elif score >= 5:
            color = "yellow"
            rating = "MODERATE"
        else:
            color = "red"
            rating = "WEAK"
        
        # Create visual score bar
        filled = int(score)
        bar = "█" * filled + "░" * (10 - filled)
        
        score_text = Text()
        score_text.append(f"\n  OVERALL QUALITY SCORE: ", style="bold")
        score_text.append(f"{score:.1f}/10 ", style=f"bold {color}")
        score_text.append(f"[{rating}]\n", style=f"bold {color}")
        score_text.append(f"  [{bar}]\n", style=color)
        
        panel = Panel(score_text, title="[bold]Quality Assessment[/bold]", border_style=color)
        self.console.print(panel)
    
    def _print_executive_summary(self, report: QualityReport):
        """Print executive summary"""
        self.console.print("\n[bold cyan]📋 EXECUTIVE SUMMARY[/bold cyan]")
        self.console.print("─" * 50)
        self.console.print(Panel(Markdown(report.executive_summary), border_style="cyan"))
    
    def _print_category_scores(self, report: QualityReport):
        """Print category-wise scores"""
        self.console.print("\n[bold cyan]📊 CATEGORY SCORES[/bold cyan]")
        self.console.print("─" * 50)
        
        table = Table(show_header=True, header_style="bold white", box=None)
        table.add_column("Category", style="dim", width=35)
        table.add_column("Score", justify="center", width=10)
        table.add_column("Rating", justify="center", width=15)
        table.add_column("Bar", width=12)
        
        for cs in report.category_scores:
            color = self._get_score_color(cs.score)
            rating = self._get_rating_text(cs.score)
            bar = self._create_mini_bar(cs.score)
            
            table.add_row(
                cs.category,
                f"[{color}]{cs.score:.1f}[/{color}]",
                f"[{color}]{rating}[/{color}]",
                f"[{color}]{bar}[/{color}]"
            )
        
        self.console.print(table)
    
    def _print_strengths(self, report: QualityReport):
        """Print key strengths"""
        self.console.print("\n[bold green]✓ KEY STRENGTHS[/bold green]")
        self.console.print("─" * 50)
        
        if report.key_strengths:
            for i, strength in enumerate(report.key_strengths[:8], 1):
                self.console.print(f"  [green]{i}.[/green] {strength}")
        else:
            self.console.print("  [dim]No significant strengths identified[/dim]")
    
    def _print_red_flags(self, report: QualityReport):
        """Print red flags"""
        self.console.print("\n[bold red]⚠ RED FLAGS & CONCERNS[/bold red]")
        self.console.print("─" * 50)
        
        if report.red_flags:
            for rf in report.red_flags:
                severity_color = self._get_severity_color(rf.severity)
                
                self.console.print(f"\n  [{severity_color}]● [{rf.severity.upper()}][/{severity_color}] {rf.description}")
                self.console.print(f"    [dim]Category:[/dim] {rf.category}")
                self.console.print(f"    [dim]Impact:[/dim] {rf.impact}")
                self.console.print(f"    [dim]Action:[/dim] {rf.recommendation}")
        else:
            self.console.print("  [green]No significant red flags identified[/green]")
    
    def _print_investment_thesis(self, report: QualityReport):
        """Print investment thesis"""
        self.console.print("\n[bold cyan]💡 INVESTMENT THESIS[/bold cyan]")
        self.console.print("─" * 50)
        self.console.print(Panel(Markdown(report.investment_thesis), border_style="cyan"))
    
    def _print_risk_assessment(self, report: QualityReport):
        """Print risk assessment"""
        self.console.print("\n[bold yellow]⚡ RISK ASSESSMENT[/bold yellow]")
        self.console.print("─" * 50)
        self.console.print(Panel(Markdown(report.risk_assessment), border_style="yellow"))
    
    def _print_detailed_metrics(self, report: QualityReport):
        """Print detailed metrics tables"""
        if not report.metrics_summary:
            return
        
        self.console.print("\n[bold cyan]📈 DETAILED METRICS[/bold cyan]")
        self.console.print("─" * 50)
        
        metrics = report.metrics_summary
        
        # Company Info
        info = metrics.get("company_info", {})
        if info:
            self.console.print(f"\n  [bold]Company Information[/bold]")
            self.console.print(f"    Sector: {info.get('sector', 'N/A')}")
            self.console.print(f"    Industry: {info.get('industry', 'N/A')}")
            if info.get('market_cap'):
                market_cap = info['market_cap']
                if market_cap >= 1e12:
                    cap_str = f"${market_cap/1e12:.2f}T"
                elif market_cap >= 1e9:
                    cap_str = f"${market_cap/1e9:.2f}B"
                elif market_cap >= 1e7:
                    cap_str = f"₹{market_cap/1e7:.0f} Cr"
                else:
                    cap_str = f"{market_cap:,.0f}"
                self.console.print(f"    Market Cap: {cap_str}")
        
        # Valuation Metrics
        valuation = metrics.get("valuation", {})
        if valuation:
            self.console.print(f"\n  [bold]Valuation Metrics[/bold]")
            if valuation.get('pe_ratio'):
                self.console.print(f"    P/E Ratio: {valuation['pe_ratio']:.2f}")
            if valuation.get('pb_ratio'):
                self.console.print(f"    P/B Ratio: {valuation['pb_ratio']:.2f}")
            if valuation.get('dividend_yield'):
                self.console.print(f"    Dividend Yield: {valuation['dividend_yield']:.2f}%")
        
        # Revenue and Profit Trends
        revenue = metrics.get("revenue_trend", {})
        profit = metrics.get("profit_trend", {})
        
        if revenue or profit:
            self.console.print(f"\n  [bold]Financial Trends[/bold]")
            
            if revenue:
                table = Table(show_header=True, header_style="bold", box=None)
                table.add_column("Year", style="dim")
                for year in list(revenue.keys())[:5]:
                    table.add_column(year, justify="right")
                
                rev_row = ["Revenue"]
                for year in list(revenue.keys())[:5]:
                    val = revenue[year]
                    if val >= 1e9:
                        rev_row.append(f"{val/1e9:.1f}B")
                    elif val >= 1e7:
                        rev_row.append(f"{val/1e7:.0f}Cr")
                    elif val >= 1e6:
                        rev_row.append(f"{val/1e6:.1f}M")
                    else:
                        rev_row.append(f"{val:,.0f}")
                table.add_row(*rev_row)
                
                if profit:
                    prof_row = ["Net Income"]
                    for year in list(profit.keys())[:5]:
                        val = profit[year]
                        if val >= 1e9:
                            prof_row.append(f"{val/1e9:.1f}B")
                        elif val >= 1e7:
                            prof_row.append(f"{val/1e7:.0f}Cr")
                        elif val >= 1e6:
                            prof_row.append(f"{val/1e6:.1f}M")
                        else:
                            prof_row.append(f"{val:,.0f}")
                    if len(prof_row) == len(table.columns):
                        table.add_row(*prof_row)
                
                self.console.print(table)
        
        # Key Ratios
        returns = metrics.get("returns", {})
        if returns:
            self.console.print(f"\n  [bold]Return Metrics (Latest Available)[/bold]")
            for metric_name, values in returns.items():
                if values:
                    latest = list(values.values())[0] if isinstance(values, dict) else values
                    if isinstance(latest, (int, float)):
                        self.console.print(f"    {metric_name.upper()}: {latest:.1f}%")
    
    def _get_score_color(self, score: float) -> str:
        """Get color based on score"""
        if score >= 7:
            return "green"
        elif score >= 5:
            return "yellow"
        else:
            return "red"
    
    def _get_rating_text(self, score: float) -> str:
        """Get rating text based on score"""
        if score >= 8:
            return "Excellent"
        elif score >= 7:
            return "Strong"
        elif score >= 6:
            return "Good"
        elif score >= 5:
            return "Moderate"
        elif score >= 4:
            return "Fair"
        else:
            return "Weak"
    
    def _create_mini_bar(self, score: float) -> str:
        """Create mini score bar"""
        filled = int(score)
        return "█" * filled + "░" * (10 - filled)
    
    def _get_severity_color(self, severity: str) -> str:
        """Get color based on severity"""
        return {
            "High": "red",
            "Medium": "yellow",
            "Low": "blue"
        }.get(severity, "white")
    
    def to_json(self, report: QualityReport) -> str:
        """Convert report to JSON string"""
        return json.dumps({
            "company_name": report.company_name,
            "ticker": report.ticker,
            "analysis_date": report.analysis_date,
            "years_analyzed": report.years_analyzed,
            "overall_score": report.overall_score,
            "category_scores": [
                {
                    "category": cs.category,
                    "score": cs.score,
                    "strengths": cs.strengths,
                    "concerns": cs.concerns
                }
                for cs in report.category_scores
            ],
            "key_strengths": report.key_strengths,
            "red_flags": [
                {
                    "severity": rf.severity,
                    "category": rf.category,
                    "description": rf.description,
                    "impact": rf.impact,
                    "recommendation": rf.recommendation
                }
                for rf in report.red_flags
            ],
            "executive_summary": report.executive_summary,
            "investment_thesis": report.investment_thesis,
            "risk_assessment": report.risk_assessment,
            "metrics_summary": report.metrics_summary
        }, indent=2)
    
    def to_markdown(self, report: QualityReport) -> str:
        """Convert report to Markdown format"""
        md = []
        
        # Header
        md.append(f"# Quality Management Analysis Report")
        md.append(f"\n**Company:** {report.company_name} ({report.ticker})")
        md.append(f"**Analysis Date:** {report.analysis_date[:10]}")
        md.append(f"**Years Analyzed:** {report.years_analyzed}")
        
        # Overall Score
        rating = "Strong" if report.overall_score >= 7 else "Moderate" if report.overall_score >= 5 else "Weak"
        md.append(f"\n## Overall Quality Score: {report.overall_score}/10 ({rating})")
        
        # Executive Summary
        if report.executive_summary:
            md.append(f"\n## Executive Summary\n\n{report.executive_summary}")
        
        # Category Scores
        md.append("\n## Category Scores\n")
        md.append("| Category | Score | Rating |")
        md.append("|----------|-------|--------|")
        for cs in report.category_scores:
            rating = self._get_rating_text(cs.score)
            md.append(f"| {cs.category} | {cs.score:.1f}/10 | {rating} |")
        
        # Key Strengths
        md.append("\n## Key Strengths\n")
        for i, strength in enumerate(report.key_strengths[:8], 1):
            md.append(f"{i}. {strength}")
        
        # Red Flags
        md.append("\n## Red Flags & Concerns\n")
        if report.red_flags:
            for rf in report.red_flags:
                md.append(f"\n### [{rf.severity}] {rf.description}")
                md.append(f"- **Category:** {rf.category}")
                md.append(f"- **Impact:** {rf.impact}")
                md.append(f"- **Recommendation:** {rf.recommendation}")
        else:
            md.append("No significant red flags identified.")
        
        # Investment Thesis
        if report.investment_thesis:
            md.append(f"\n## Investment Thesis\n\n{report.investment_thesis}")
        
        # Risk Assessment
        if report.risk_assessment:
            md.append(f"\n## Risk Assessment\n\n{report.risk_assessment}")
        
        return "\n".join(md)
    
    def save_report(self, report: QualityReport, filepath: str, format: str = "json"):
        """Save report to file"""
        if format == "json":
            content = self.to_json(report)
        elif format == "md" or format == "markdown":
            content = self.to_markdown(report)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        self.console.print(f"[green]Report saved to:[/green] {filepath}")


class ProgressDisplay:
    """Display progress for long-running operations"""
    
    def __init__(self):
        self.console = Console()
    
    def show_fetching_progress(self, company: str):
        """Show progress while fetching data"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        ) as progress:
            task = progress.add_task(f"Fetching data for {company}...", total=None)
            return progress, task
    
    def print_status(self, message: str, style: str = ""):
        """Print status message"""
        if style:
            self.console.print(f"[{style}]{message}[/{style}]")
        else:
            self.console.print(message)
    
    def print_error(self, message: str):
        """Print error message"""
        self.console.print(f"[bold red]Error:[/bold red] {message}")
    
    def print_success(self, message: str):
        """Print success message"""
        self.console.print(f"[bold green]✓[/bold green] {message}")
    
    def print_warning(self, message: str):
        """Print warning message"""
        self.console.print(f"[bold yellow]⚠[/bold yellow] {message}")
