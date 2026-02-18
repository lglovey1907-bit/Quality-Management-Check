"""
Quality Management Analysis AI Agent
Main entry point and orchestration
"""

import os
import sys
from typing import Optional

from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

from .data_fetcher import MultiSourceFetcher, FinancialData
from .analyzer import QualityAnalyzer, AIEnhancedAnalyzer, QualityReport
from .forensic_analyzer import ForensicQualityAnalyzer
from .report_generator import ReportFormatter, ProgressDisplay
from .pdf_parser import PDFReportParser, parse_multiple_reports


# Load environment variables
load_dotenv()


class QualityManagementAgent:
    """
    AI Agent for Company Quality Management Analysis
    
    This agent:
    1. Takes input from user about company name and analysis period
    2. Fetches financial data from multiple sources (Screener.in, Yahoo Finance, etc.)
    3. Analyzes the data for quality management indicators
    4. Provides a comprehensive report with scores, strengths, and red flags
    """
    
    def __init__(self, use_ai: bool = True, pdf_mode: bool = False, use_forensic: bool = True):
        """
        Initialize the agent
        
        Args:
            use_ai: Whether to use AI-enhanced analysis (requires OpenAI API key)
            pdf_mode: Whether to use PDF upload mode instead of online fetching
            use_forensic: Whether to use forensic-grade analysis for PDFs (default: True)
        """
        self.console = Console()
        self.progress_display = ProgressDisplay()
        self.report_formatter = ReportFormatter()
        self.pdf_mode = pdf_mode
        self.use_forensic = use_forensic
        
        # Initialize data fetcher
        fmp_api_key = os.getenv("FMP_API_KEY")
        self.data_fetcher = MultiSourceFetcher(fmp_api_key=fmp_api_key)
        
        # Initialize PDF parser if in PDF mode
        if pdf_mode:
            openai_key = os.getenv("OPENAI_API_KEY")
            if not openai_key:
                raise ValueError("PDF mode requires OPENAI_API_KEY to be set for data extraction")
            self.pdf_parser = PDFReportParser(openai_key)
            # Initialize forensic analyzer for advanced PDF analysis
            if use_forensic:
                self.forensic_analyzer = ForensicQualityAnalyzer(use_ai=True)
        
        # Initialize analyzer
        self.use_ai = use_ai and os.getenv("OPENAI_API_KEY")
        if self.use_ai:
            self.analyzer = AIEnhancedAnalyzer()
        else:
            self.analyzer = QualityAnalyzer()
    
    def run_interactive(self):
        """Run the agent in interactive mode"""
        self._print_welcome()
        
        while True:
            try:
                if self.pdf_mode:
                    # PDF upload mode
                    report = self._analyze_from_pdf_interactive()
                else:
                    # Online fetching mode
                    company, years = self._get_user_input()
                    
                    if company.lower() in ['quit', 'exit', 'q']:
                        self.console.print("\n[cyan]Thank you for using Quality Management Agent. Goodbye![/cyan]\n")
                        break
                    
                    report = self.analyze_company(company, years)
                
                if report:
                    # Display report
                    self.report_formatter.print_report(report, detailed=True)
                    
                    # Ask if user wants to save
                    if Confirm.ask("\nWould you like to save this report?", default=False):
                        self._save_report(report)
                
                # Ask if user wants to analyze another company
                if not Confirm.ask("\nWould you like to analyze another company?", default=True):
                    self.console.print("\n[cyan]Thank you for using Quality Management Agent. Goodbye![/cyan]\n")
                    break
                    
            except KeyboardInterrupt:
                self.console.print("\n\n[yellow]Analysis interrupted by user[/yellow]")
                break
            except Exception as e:
                self.progress_display.print_error(str(e))
                if Confirm.ask("Would you like to try again?", default=True):
                    continue
                break
    
    def analyze_company(
        self, 
        company_identifier: str, 
        years: int = 5,
        market: str = "auto",
        save_path: Optional[str] = None
    ) -> Optional[QualityReport]:
        """
        Analyze a company's quality management
        
        Args:
            company_identifier: Company name, ticker, or identifier
            years: Number of years to analyze (default: 5)
            market: Market/source preference ('india', 'us', 'global', 'auto')
            save_path: Optional path to save the report
            
        Returns:
            QualityReport object or None if analysis fails
        """
        self.console.print()
        
        # Step 1: Search and fetch data
        self.console.print(f"[bold cyan]🔍 Searching for:[/bold cyan] {company_identifier}")
        
        # Use the identifier directly - don't rely on search which can be buggy
        ticker = company_identifier.strip()
        
        # Optionally search for company name display
        search_results = self.data_fetcher.search_company(company_identifier)
        if search_results and search_results[0].get('ticker'):
            found_ticker = search_results[0]['ticker']
            # Only use search result if it looks valid (not empty, not 'consolidated', etc.)
            if found_ticker and len(found_ticker) >= 2 and found_ticker.upper() not in ['CONSOLIDATED', 'STANDALONE']:
                self.console.print(f"[dim]Found: {search_results[0]['name']} ({found_ticker})[/dim]")
                ticker = found_ticker
            else:
                self.console.print(f"[dim]Using ticker: {ticker}[/dim]")
        else:
            self.console.print(f"[dim]Using ticker: {ticker}[/dim]")
        
        # Fetch financial data
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        ) as progress:
            progress.add_task(f"Fetching financial data...", total=None)
            fin_data = self.data_fetcher.fetch_data(ticker, years, market)
        
        if not fin_data:
            self.progress_display.print_error(f"Could not fetch data for '{company_identifier}'")
            self.console.print("[dim]Tips:[/dim]")
            self.console.print("[dim]  - For Indian stocks: Use NSE ticker (e.g., 'TCS', 'RELIANCE', 'INFY')[/dim]")
            self.console.print("[dim]  - For US stocks: Use ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')[/dim]")
            self.console.print("[dim]  - You can also add exchange suffix: 'TCS.NS' for NSE, 'AAPL' for NYSE[/dim]")
            return None
        
        self.progress_display.print_success(f"Data fetched from {fin_data.data_source}")
        
        # Step 2: Analyze data
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        ) as progress:
            task_desc = "Analyzing with AI..." if self.use_ai else "Analyzing financial data..."
            progress.add_task(task_desc, total=None)
            report = self.analyzer.analyze(fin_data)
        
        self.progress_display.print_success("Analysis complete")
        
        # Save if requested
        if save_path:
            self.report_formatter.save_report(report, save_path)
        
        return report
    
    def _print_welcome(self):
        """Print welcome message"""
        welcome_text = Text()
        welcome_text.append("\n")
        welcome_text.append("╔══════════════════════════════════════════════════════════════╗\n", style="cyan")
        welcome_text.append("║                                                              ║\n", style="cyan")
        welcome_text.append("║  ", style="cyan")
        welcome_text.append("    QUALITY MANAGEMENT ANALYSIS AI AGENT", style="bold white")
        welcome_text.append("              ║\n", style="cyan")
        welcome_text.append("║                                                              ║\n", style="cyan")
        welcome_text.append("║  ", style="cyan")
        welcome_text.append("  Analyze companies for quality management indicators", style="dim white")
        welcome_text.append("     ║\n", style="cyan")
        welcome_text.append("║  ", style="cyan")
        welcome_text.append("  Get scores, strengths, and red flag predictions", style="dim white")
        welcome_text.append("        ║\n", style="cyan")
        welcome_text.append("║                                                              ║\n", style="cyan")
        welcome_text.append("╚══════════════════════════════════════════════════════════════╝\n", style="cyan")
        
        self.console.print(welcome_text)
        
        # Print mode and data sources
        if self.pdf_mode:
            self.console.print("[dim]Mode: PDF Upload - Extract data from annual report PDFs[/dim]")
            self.console.print("[dim]Required: OpenAI API key for PDF extraction[/dim]")
        else:
            self.console.print("[dim]Mode: Online Fetching - Screener.in (India), Yahoo Finance (Global)[/dim]")
        
        if self.use_ai:
            self.console.print("[dim]AI Analysis: Enabled (OpenAI)[/dim]")
        else:
            self.console.print("[dim]AI Analysis: Disabled (set OPENAI_API_KEY to enable)[/dim]")
        self.console.print()
    
    def _get_user_input(self) -> tuple:
        """Get company name and years from user"""
        self.console.print("[bold]Enter company details:[/bold]")
        
        company = Prompt.ask(
            "  Company name or ticker",
            default=""
        ).strip()
        
        if company.lower() in ['quit', 'exit', 'q']:
            return company, 0
        
        while not company:
            company = Prompt.ask(
                "  [red]Please enter a company name or ticker[/red]",
                default=""
            ).strip()
        
        years = IntPrompt.ask(
            "  Number of years to analyze",
            default=5
        )
        
        # Validate years
        years = max(1, min(10, years))
        
        return company, years
    
    def _analyze_from_pdf_interactive(self) -> Optional[QualityReport]:
        """Interactive mode for PDF upload"""
        self.console.print("[bold]Upload Annual Report(s):[/bold]")
        
        # Get company name
        company_name = Prompt.ask("  Company name").strip()
        if not company_name:
            self.progress_display.print_error("Company name is required")
            return None
        
        # Ask for single or multiple PDFs
        mode = Prompt.ask(
            "  Upload mode",
            choices=["single", "multiple"],
            default="single"
        )
        
        pdf_paths = []
        
        if mode == "single":
            # Single PDF with multiple years
            pdf_path = Prompt.ask("  Path to annual report PDF").strip()
            if not os.path.exists(pdf_path):
                self.progress_display.print_error(f"File not found: {pdf_path}")
                return None
            
            years = IntPrompt.ask("  How many years of data to extract", default=5)
            pdf_paths = [pdf_path]
            years_to_extract = years
            
        else:
            # Multiple PDFs (one per year)
            num_reports = IntPrompt.ask("  Number of annual reports", default=3)
            
            for i in range(num_reports):
                pdf_path = Prompt.ask(f"  Path to report {i+1} (most recent first)").strip()
                if os.path.exists(pdf_path):
                    pdf_paths.append(pdf_path)
                else:
                    self.console.print(f"[yellow]Skipping {pdf_path} - file not found[/yellow]")
            
            if not pdf_paths:
                self.progress_display.print_error("No valid PDF files provided")
                return None
            
            years_to_extract = len(pdf_paths)
        
        # Extract data from PDF(s)
        self.console.print()
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        ) as progress:
            progress.add_task("Extracting data from PDF...", total=None)
            
            try:
                if len(pdf_paths) == 1:
                    fin_data = self.pdf_parser.parse_annual_report(
                        pdf_paths[0], 
                        company_name, 
                        years_to_extract
                    )
                else:
                    fin_data = parse_multiple_reports(
                        pdf_paths, 
                        company_name,
                        os.getenv("OPENAI_API_KEY")
                    )
            except Exception as e:
                self.progress_display.print_error(f"Failed to extract data: {e}")
                return None
        
        if not fin_data or (not fin_data.revenue and not fin_data.net_income):
            self.progress_display.print_error("Could not extract sufficient financial data from PDF")
            return None
        
        self.progress_display.print_success("Data extracted from PDF")
        
        # Analyze data
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        ) as progress:
            task_desc = "Analyzing with AI..." if self.use_ai else "Analyzing financial data..."
            progress.add_task(task_desc, total=None)
            report = self.analyzer.analyze(fin_data)
        
        self.progress_display.print_success("Analysis complete")
        
        return report
    
    def analyze_from_pdf(
        self,
        pdf_path: str,
        company_name: str,
        years: int = 5,
        save_path: Optional[str] = None
    ) -> Optional[QualityReport]:
        """
        Analyze company from PDF annual report
        
        Args:
            pdf_path: Path to the PDF annual report
            company_name: Name of the company
            years: Number of years to extract (default: 5)
            save_path: Optional path to save the report
            
        Returns:
            QualityReport object or None if analysis fails
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Extract data
        self.console.print(f"[bold cyan]📄 Extracting data from:[/bold cyan] {pdf_path}")
        
        try:
            # If using forensic analysis, extract full PDF text and use advanced prompt
            if self.use_forensic and hasattr(self, 'forensic_analyzer'):
                self.console.print("[bold magenta]🔬 Using Forensic Analysis Mode[/bold magenta]")
                
                # Extract full PDF text for forensic analysis
                pdf_text = self.pdf_parser.extract_text_from_pdf(pdf_path)
                
                # Use forensic analyzer with comprehensive prompt
                report = self.forensic_analyzer.analyze_from_pdf_text(
                    pdf_text=pdf_text,
                    company_name=company_name,
                    years_analyzed=years
                )
                
                self.progress_display.print_success("Forensic analysis completed successfully")
            else:
                # Traditional analysis: extract structured data then analyze
                fin_data = self.pdf_parser.parse_annual_report(pdf_path, company_name, years)
                
                if not fin_data or (not fin_data.revenue and not fin_data.net_income):
                    self.progress_display.print_error("Could not extract sufficient financial data")
                    return None
                
                self.progress_display.print_success("Data extracted successfully")
                
                # Analyze with traditional method
                report = self.analyzer.analyze(fin_data)
            
        except Exception as e:
            self.progress_display.print_error(f"Failed to analyze: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        if save_path:
            self.report_formatter.save_report(report, save_path)
        
        return report
    
    def _save_report(self, report):
        """Save report to file"""
        format_choice = Prompt.ask(
            "  Save format",
            choices=["json", "markdown", "both"],
            default="json"
        )
        
        base_filename = f"quality_report_{report.ticker}_{report.analysis_date[:10]}"
        
        if format_choice in ["json", "both"]:
            json_path = f"reports/{base_filename}.json"
            os.makedirs("reports", exist_ok=True)
            self.report_formatter.save_report(report, json_path, "json")
        
        if format_choice in ["markdown", "both"]:
            md_path = f"reports/{base_filename}.md"
            os.makedirs("reports", exist_ok=True)
            self.report_formatter.save_report(report, md_path, "md")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Quality Management Analysis AI Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Online mode (default)
  python -m src.agent                          # Interactive mode
  python -m src.agent --company RELIANCE       # Analyze Reliance
  python -m src.agent --company AAPL --years 3 # Analyze Apple for 3 years
  
  # PDF mode
  python -m src.agent --pdf                    # Interactive PDF mode
  python -m src.agent --pdf-file report.pdf --company "ABC Corp" --years 5
  python -m src.agent --pdf-files report1.pdf report2.pdf --company "ABC Corp"
        """
    )
    
    # Mode selection
    parser.add_argument(
        "--pdf",
        action="store_true",
        help="Use PDF upload mode instead of online fetching"
    )
    
    parser.add_argument(
        "--pdf-file",
        type=str,
        help="Path to single PDF annual report (use with --company)"
    )
    
    parser.add_argument(
        "--pdf-files",
        nargs='+',
        help="Paths to multiple PDF annual reports (one per year, most recent first)"
    )
    
    parser.add_argument(
        "--company", "-c",
        type=str,
        help="Company name or ticker symbol (or company name for PDF mode)"
    )
    
    parser.add_argument(
        "--years", "-y",
        type=int,
        default=5,
        help="Number of years to analyze (default: 5)"
    )
    
    parser.add_argument(
        "--market", "-m",
        type=str,
        choices=["india", "us", "global", "auto"],
        default="auto",
        help="Market/source preference (default: auto) - Online mode only"
    )
    
    parser.add_argument(
        "--save", "-s",
        action="store_true",
        help="Save report to file"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file path"
    )
    
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Disable AI-enhanced analysis"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    
    args = parser.parse_args()
    
    # Determine if PDF mode
    pdf_mode = args.pdf or args.pdf_file or args.pdf_files
    
    # Initialize agent
    agent = QualityManagementAgent(use_ai=not args.no_ai, pdf_mode=pdf_mode)
    
    # Non-interactive mode
    if args.pdf_file:
        # Single PDF file mode
        if not args.company:
            print("Error: --company is required when using --pdf-file")
            return
        
        save_path = args.output
        if args.save and not save_path:
            os.makedirs("reports", exist_ok=True)
            safe_name = args.company.replace(" ", "_")
            save_path = f"reports/quality_report_{safe_name}.json"
        
        report = agent.analyze_from_pdf(
            args.pdf_file,
            args.company,
            years=args.years,
            save_path=save_path
        )
        
        if report:
            if args.json:
                print(agent.report_formatter.to_json(report))
            else:
                agent.report_formatter.print_report(report)
    
    elif args.pdf_files:
        # Multiple PDF files mode
        if not args.company:
            print("Error: --company is required when using --pdf-files")
            return
        
        from .pdf_parser import parse_multiple_reports
        
        agent.console.print(f"[bold cyan]📄 Extracting data from {len(args.pdf_files)} PDF files[/bold cyan]")
        
        try:
            fin_data = parse_multiple_reports(
                args.pdf_files,
                args.company,
                os.getenv("OPENAI_API_KEY")
            )
        except Exception as e:
            agent.progress_display.print_error(f"Failed to extract data: {e}")
            return
        
        agent.progress_display.print_success("Data extracted successfully")
        
        report = agent.analyzer.analyze(fin_data)
        
        if args.save or args.output:
            save_path = args.output
            if not save_path:
                os.makedirs("reports", exist_ok=True)
                safe_name = args.company.replace(" ", "_")
                save_path = f"reports/quality_report_{safe_name}.json"
            agent.report_formatter.save_report(report, save_path)
        
        if report:
            if args.json:
                print(agent.report_formatter.to_json(report))
            else:
                agent.report_formatter.print_report(report)
    
    elif args.company and not pdf_mode:
        # Online fetching mode (non-interactive)
        save_path = args.output
        if args.save and not save_path:
            os.makedirs("reports", exist_ok=True)
            save_path = f"reports/quality_report_{args.company}.json"
        
        report = agent.analyze_company(
            args.company,
            years=args.years,
            market=args.market,
            save_path=save_path
        )
        
        if report:
            if args.json:
                print(agent.report_formatter.to_json(report))
            else:
                agent.report_formatter.print_report(report)
    else:
        # Interactive mode
        agent.run_interactive()


if __name__ == "__main__":
    main()
