"""
Installation script for PDF Reports & Dashboard enhancements
Run this script to install the new dependencies
"""

import subprocess
import sys

def install_packages():
    """Install required packages for PDF and dashboard features"""
    
    print("=" * 60)
    print("  Quality Management Analysis - Setup Script")
    print("  Installing PDF & Dashboard Dependencies")
    print("=" * 60)
    print()
    
    packages = [
        "reportlab>=4.0.0",
        "matplotlib>=3.8.0",
        "plotly>=5.18.0",
        "kaleido>=0.2.1"
    ]
    
    print("📦 Installing required packages...")
    print()
    
    try:
        for package in packages:
            print(f"Installing {package}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package, "-q"
            ])
        
        print()
        print("=" * 60)
        print("  ✅ Installation Successful!")
        print("=" * 60)
        print()
        print("New features installed:")
        print("  📄 Institutional PDF Report Generator")
        print("  📊 Interactive Dashboard Charts")
        print("  🎯 Red Flag Alert System")
        print("  📈 Visual Analytics")
        print()
        print("To start the application:")
        print("  streamlit run app.py")
        print()
        print("Documentation: PDF_DASHBOARD_GUIDE.md")
        print("=" * 60)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print()
        print("=" * 60)
        print("  ❌ Installation Failed")
        print("=" * 60)
        print()
        print("Please try manually:")
        print("  pip install reportlab matplotlib plotly kaleido")
        print()
        print("Or install from requirements.txt:")
        print("  pip install -r requirements.txt")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = install_packages()
    sys.exit(0 if success else 1)
