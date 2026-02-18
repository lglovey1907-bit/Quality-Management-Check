#!/bin/bash

# Installation script for PDF Reports & Dashboard enhancements
# Run this script to install the new dependencies

echo "================================================"
echo "  Quality Management Analysis - Setup Script"
echo "  Installing PDF & Dashboard Dependencies"
echo "================================================"
echo ""

# Check if pip is available
if ! command -v pip &> /dev/null; then
    echo "❌ Error: pip is not installed"
    echo "Please install Python and pip first"
    exit 1
fi

echo "📦 Installing required packages..."
echo ""

# Install packages
pip install reportlab>=4.0.0 matplotlib>=3.8.0 plotly>=5.18.0 kaleido>=0.2.1

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "================================================"
    echo "  ✅ Installation Successful!"
    echo "================================================"
    echo ""
    echo "New features installed:"
    echo "  📄 Institutional PDF Report Generator"
    echo "  📊 Interactive Dashboard Charts"
    echo "  🎯 Red Flag Alert System"
    echo "  📈 Visual Analytics"
    echo ""
    echo "To start the application:"
    echo "  streamlit run app.py"
    echo ""
    echo "Documentation: PDF_DASHBOARD_GUIDE.md"
    echo "================================================"
else
    echo ""
    echo "================================================"
    echo "  ❌ Installation Failed"
    echo "================================================"
    echo ""
    echo "Please try manually:"
    echo "  pip install reportlab matplotlib plotly kaleido"
    echo ""
    echo "Or install from requirements.txt:"
    echo "  pip install -r requirements.txt"
    echo "================================================"
    exit 1
fi
