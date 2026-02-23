#!/usr/bin/env python3
"""Quick test to verify ALKEM.NS validation works"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
load_dotenv()

# Import the validation function
from data_fetcher import validate_company_name

fmp_api_key = os.getenv("FMP_API_KEY")

print("=" * 80)
print("Testing ALKEM.NS Validation")
print("=" * 80)

test_cases = [
    "ALKEM.NS",
    "alkem.ns",
    "ALKEM",
    "TCS.NS",
    "RANDOMSTOCK.NS"  # Should be accepted even if not in list
]

for test in test_cases:
    print(f"\n{'='*80}")
    print(f"Input: '{test}'")
    print('-' * 80)
    
    result = validate_company_name(test, fmp_api_key)
    
    print(f"Valid: {result['valid']}")
    if result['valid'] and result['best_match']:
        print(f"Name: {result['best_match']['name']}")
        print(f"Ticker: {result['best_match']['ticker']}")
    if result.get('error'):
        print(f"Error: {result['error']}")
    if result.get('note'):
        print(f"Note: {result['note']}")
    
print(f"\n{'='*80}")
print("Test Complete!")
print("=" * 80)
