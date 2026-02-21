"""
Test script for company name validation functionality
"""
import os
from dotenv import load_dotenv
from src.data_fetcher import validate_company_name

# Load environment variables
load_dotenv()

def test_validation():
    """Test company validation with FMP API"""
    fmp_api_key = os.getenv("FMP_API_KEY")
    
    # Test cases
    test_companies = [
        "Apple",
        "Reliance Industries",
        "Microsoft",
        "InvalidCompanyXYZ123"
    ]
    
    print("="*60)
    print("Testing Company Name Validation")
    print("="*60)
    
    for company in test_companies:
        print(f"\n🔍 Searching for: {company}")
        result = validate_company_name(company, fmp_api_key)
        
        if result['valid']:
            print(f"✅ Valid - Found {len(result['matches'])} matches")
            print(f"   Best Match: {result['best_match']['name']} ({result['best_match']['ticker']})")
            if len(result['matches']) > 1:
                print(f"   Other matches:")
                for match in result['matches'][1:4]:  # Show up to 3 more
                    print(f"      - {match['name']} ({match['ticker']})")
        else:
            print(f"❌ Invalid - {result['error']}")
    
    print("\n" + "="*60)
    print("Test completed!")
    print("="*60)

if __name__ == "__main__":
    test_validation()
