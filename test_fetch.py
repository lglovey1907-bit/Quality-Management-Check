#!/usr/bin/env python3
"""Test script to verify data fetching works correctly"""

import sys
sys.path.insert(0, '/workspaces/Quality-Management-Check')

from src.data_fetcher import MultiSourceFetcher

def test_company(fetcher, ticker, years=3):
    print(f"\n{'='*50}")
    print(f"Testing: {ticker}")
    print('='*50)
    
    data = fetcher.fetch_data(ticker, years)
    
    if data:
        print(f"  SUCCESS!")
        print(f"  Company: {data.company_name}")
        print(f"  Ticker: {data.ticker}")
        print(f"  Source: {data.data_source}")
        print(f"  Revenue years: {list(data.revenue.keys())}")
        if data.revenue:
            latest_year = list(data.revenue.keys())[0]
            print(f"  Latest Revenue: {data.revenue[latest_year]:,.0f}")
        return True
    else:
        print(f"  FAILED - No data returned")
        return False

if __name__ == "__main__":
    fetcher = MultiSourceFetcher()
    
    # Test cases
    test_cases = [
        "TCS",         # Indian stock
        "RELIANCE",    # Indian stock
        "AAPL",        # US stock
    ]
    
    results = {}
    for ticker in test_cases:
        results[ticker] = test_company(fetcher, ticker)
    
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    for ticker, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {ticker}: {status}")
