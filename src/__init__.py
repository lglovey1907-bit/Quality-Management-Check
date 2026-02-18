"""
Quality Management Analysis AI Agent

A comprehensive AI agent for analyzing companies' quality management
through financial data analysis.
"""

from .data_fetcher import (
    FinancialData,
    ScreenerInFetcher,
    YahooFinanceFetcher,
    FMPFetcher,
    MultiSourceFetcher,
    DataFetcherFactory
)

from .analyzer import (
    QualityAnalyzer,
    AIEnhancedAnalyzer,
    QualityReport,
    QualityScore,
    RedFlag,
    ScoreCategory
)

from .report_generator import (
    ReportFormatter,
    ProgressDisplay
)

from .pdf_report_generator import (
    InstitutionalReportGenerator,
    generate_institutional_pdf
)

from .pdf_compressor import (
    PDFCompressor,
    compress_pdf_for_upload,
    format_size
)

from .pdf_parser import (
    PDFReportParser,
    parse_multiple_reports
)

from .agent import (
    QualityManagementAgent,
    main
)

__version__ = "1.0.0"
__author__ = "Quality Management AI Agent"

__all__ = [
    # Data Fetching
    "FinancialData",
    "ScreenerInFetcher",
    "YahooFinanceFetcher",
    "FMPFetcher",
    "MultiSourceFetcher",
    "DataFetcherFactory",
    
    # PDF Parsing
    "PDFReportParser",
    "parse_multiple_reports",
    
    # Analysis
    "QualityAnalyzer",
    "AIEnhancedAnalyzer",
    "QualityReport",
    "QualityScore",
    "RedFlag",
    "ScoreCategory",
    
    # Reporting
    "ReportFormatter",
    "ProgressDisplay",
    
    # Agent
    "QualityManagementAgent",
    "main"
]
