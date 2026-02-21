"""
Test script for company name validation functionality
Tests both company names and ticker symbols
"""
import os
from dotenv import load_dotenv
from src.data_fetcher import validate_company_name

# Load environment variables
load_dotenv()

def test_validation():
    """Test company validation with FMP API - company names and tickers"""
    fmp_api_key = os.getenv("FMP_API_KEY")
    
    # Test cases - mix of company names and tickers
    test_cases = [
        ("Apple", "Company Name"),
        ("AAPL", "Ticker"),
        ("Reliance Industries", "Company Name"),
        ("TCS", "Ticker (Indian)"),
        ("Microsoft", "Company Name"),
        ("MSFT", "Ticker"),
        ("InvalidCompanyXYZ123", "Invalid Input")
    ]
    
    print("="*70)
    print("Testing Company Name/Ticker Validation")
    print("="*70)
    
    for query, input_type in test_cases:
        print(f"\n🔍 Testing: {query} ({input_type})")
        print("-" * 70)
        result = validate_company_name(query, fmp_api_key)
        
        if result['valid']:
            print(f"✅ Valid - Found {len(result['matches'])} match(es)")
            print(f"\n   Best Match:")
            best = result['best_match']
            print(f"   📊 Company: {best['name']}")
            print(f"   🎫 Ticker: {best['ticker']}")
            
            if len(result['matches']) > 1:
                print(f"\n   Other matches:")
                for match in result['matches'][1:4]:  # Show up to 3 more
                    print(f"      • {match['name']} ({match['ticker']})")
        else:
            print(f"❌ Invalid - {result['error']}")
    
    print("\n" + "="*70)
    print("Test completed!")
    print("="*70)
    
    # Test specific case mentioned by user
    print("\n\n" + "="*70)
    print("Testing TCS (the specific case from user)")
    print("="*70)
    result = validate_company_name("TCS", fmp_api_key)
    if result['valid']:
        print("\n✅ TCS Validation Results:")
        for i, match in enumerate(result['matches'], 1):
            print(f"   {i}. {match['name']} ({match['ticker']})")
    print("="*70)

if __name__ == "__main__":
    test_validation()
