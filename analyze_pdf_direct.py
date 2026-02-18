#!/usr/bin/env python3
"""
WORKAROUND: Direct PDF Analysis without Web Upload

This script bypasses the web upload interface and directly analyzes PDF files.
Use this if you're experiencing "AxiosError: Network Error" in the web app.

Usage:
    python analyze_pdf_direct.py path/to/report.pdf "Company Name"
    
    # Multiple PDFs:
    python analyze_pdf_direct.py report1.pdf report2.pdf report3.pdf "Company Name"
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src import QualityManagementAgent, ReportFormatter, parse_multiple_reports
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your-openai-api-key-here":
        print("❌ ERROR: OPENAI_API_KEY not configured")
        print("Please set your OpenAI API key in the .env file")
        sys.exit(1)
    
    # Parse arguments
    if len(sys.argv) < 3:
        print("Usage: python analyze_pdf_direct.py <pdf_file(s)> <company_name>")
        print("\nExamples:")
        print('  python analyze_pdf_direct.py report.pdf "ABC Corporation"')
        print('  python analyze_pdf_direct.py r1.pdf r2.pdf r3.pdf "XYZ Corp"')
        sys.exit(1)
    
    company_name = sys.argv[-1]  # Last argument is company name
    pdf_files = sys.argv[1:-1]    # All other arguments are PDF files
    
    # Verify files exist
    for pdf_file in pdf_files:
        if not os.path.exists(pdf_file):
            print(f"❌ ERROR: File not found: {pdf_file}")
            sys.exit(1)
        
        file_size_mb = os.path.getsize(pdf_file) / (1024 * 1024)
        print(f"📄 {pdf_file}: {file_size_mb:.2f}MB")
    
    print(f"\n🏢 Company: {company_name}")
    print(f"📊 Analyzing {len(pdf_files)} PDF file(s)...")
    print()
    
    try:
        # Initialize agent in PDF mode
        agent = QualityManagementAgent(use_ai=True, pdf_mode=True)
        
        # Analyze
        if len(pdf_files) == 1:
            print(f"🤖 Extracting data from {pdf_files[0]}...")
            report = agent.analyze_from_pdf(
                pdf_path=pdf_files[0],
                company_name=company_name,
                years=5
            )
        else:
            print(f"🤖 Extracting data from {len(pdf_files)} PDFs...")
            financial_data = parse_multiple_reports(pdf_files, company_name)
            report = agent.analyzer.analyze(financial_data)
        
        print("\n✅ Analysis complete!\n")
        
        # Display report
        formatter = ReportFormatter()
        formatter.print_report(report)
        
        print("\n" + "="*70)
        print("✅ SUCCESS! Analysis completed without upload errors.")
        print("="*70)
        
        # Optionally save
        save = input("\n💾 Save report to file? (y/n): ").strip().lower()
        if save == 'y':
            import json
            from datetime import datetime
            
            filename = f"{company_name.replace(' ', '_')}_analysis_{datetime.now().strftime('%Y%m%d')}.json"
            
            # Extract category scores into a dict
            category_scores_dict = {}
            if hasattr(report, 'category_scores') and report.category_scores:
                for cat_score in report.category_scores:
                    category_scores_dict[cat_score.category] = cat_score.score
            
            # Convert red flags to dict if they're objects
            red_flags_list = []
            if report.red_flags:
                for flag in report.red_flags:
                    if isinstance(flag, str):
                        red_flags_list.append(flag)
                    else:
                        # If it's a RedFlag object
                        red_flags_list.append({
                            'severity': getattr(flag, 'severity', ''),
                            'category': getattr(flag, 'category', ''),
                            'description': getattr(flag, 'description', ''),
                            'impact': getattr(flag, 'impact', ''),
                            'recommendation': getattr(flag, 'recommendation', '')
                        })
            
            report_dict = {
                'company_name': company_name,
                'ticker': report.ticker,
                'analysis_date': report.analysis_date,
                'years_analyzed': report.years_analyzed,
                'overall_score': report.overall_score,
                'category_scores': category_scores_dict,
                'key_strengths': report.key_strengths,
                'red_flags': red_flags_list,
                'executive_summary': report.executive_summary if report.executive_summary else '',
                'export_timestamp': datetime.now().isoformat()
            }
            
            with open(filename, 'w') as f:
                json.dump(report_dict, f, indent=2)
            
            print(f"✅ Report saved to: {filename}")
        
    except Exception as e:
        print(f"\n❌ ERROR during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
