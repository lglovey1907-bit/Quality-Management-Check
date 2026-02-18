#!/usr/bin/env python3
"""Quick test to verify QualityReport can be instantiated"""

import sys
sys.path.insert(0, '/workspaces/Quality-Management-Check')

from src.analyzer import QualityReport

print("Testing QualityReport instantiation...")

try:
    report = QualityReport(
        company_name="Test Company",
        ticker="TEST",
        analysis_date="2026-02-15",
        years_analyzed=3
    )
    print(f"✓ SUCCESS: QualityReport created")
    print(f"  Company: {report.company_name}")
    print(f"  Ticker: {report.ticker}")
    print(f"  Overall Score (default): {report.overall_score}")
    
    # Test setting the score
    report.overall_score = 7.5
    print(f"  Overall Score (updated): {report.overall_score}")
    
except Exception as e:
    print(f"✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
