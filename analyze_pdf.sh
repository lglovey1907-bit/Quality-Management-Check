#!/bin/bash

# Direct PDF Analysis - Shell Script
# Drag and drop your PDF files onto this script to analyze them

echo ""
echo "========================================"
echo "  Quality Management PDF Analyzer"
echo "========================================"
echo ""

# Check if files were provided
if [ $# -eq 0 ]; then
    echo "ERROR: No files provided"
    echo ""
    echo "USAGE:"
    echo "  ./analyze_pdf.sh file.pdf [file2.pdf ...] \"Company Name\""
    echo ""
    echo "EXAMPLE:"
    echo "  ./analyze_pdf.sh report.pdf \"ABC Corporation\""
    echo "  ./analyze_pdf.sh r1.pdf r2.pdf r3.pdf \"XYZ Ltd\""
    echo ""
    exit 1
fi

# Collect all PDF files
PDF_FILES=()
COMPANY_NAME=""

for arg in "$@"; do
    if [[ "$arg" == *.pdf ]]; then
        if [ -f "$arg" ]; then
            PDF_FILES+=("$arg")
        else
            echo "WARNING: File not found: $arg"
        fi
    else
        # Last non-PDF argument is the company name
        COMPANY_NAME="$arg"
    fi
done

# Check if we have PDF files
if [ ${#PDF_FILES[@]} -eq 0 ]; then
    echo "ERROR: No valid PDF files found"
    exit 1
fi

# If no company name provided, ask for it
if [ -z "$COMPANY_NAME" ]; then
    read -p "Enter company name: " COMPANY_NAME
fi

if [ -z "$COMPANY_NAME" ]; then
    echo "ERROR: Company name is required"
    exit 1
fi

echo "Found ${#PDF_FILES[@]} PDF file(s)"
echo "Company: $COMPANY_NAME"
echo ""
echo "Analyzing..."
echo ""

# Run the direct analysis script
python3 analyze_pdf_direct.py "${PDF_FILES[@]}" "$COMPANY_NAME"

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "✅ Analysis completed successfully!"
else
    echo ""
    echo "❌ Analysis failed with exit code: $exit_code"
fi

exit $exit_code
