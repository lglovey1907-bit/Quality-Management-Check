#!/usr/bin/env python3
"""
PDF Compression Tool - Run BEFORE uploading to web app
Compresses large PDF files to under 20MB for successful upload

Usage:
    python compress_for_upload.py input.pdf [output.pdf]
    python compress_for_upload.py large_report.pdf compressed_report.pdf
"""

import sys
import os
from pathlib import Path

def main():
    # Check if running in project directory
    try:
        from src.pdf_compressor import PDFCompressor, format_size
    except ImportError:
        print("❌ Error: Cannot import pdf_compressor")
        print("Make sure you're running this from the project directory:")
        print("  cd /workspaces/Quality-Management-Check")
        print("  python compress_for_upload.py your_file.pdf")
        sys.exit(1)
    
    # Parse arguments
    if len(sys.argv) < 2:
        print("=" * 60)
        print("  PDF Compression Tool for Upload")
        print("=" * 60)
        print()
        print("Usage:")
        print("  python compress_for_upload.py <input.pdf> [output.pdf]")
        print()
        print("Examples:")
        print("  python compress_for_upload.py annual_report.pdf")
        print("  python compress_for_upload.py report.pdf compressed_report.pdf")
        print()
        print("What it does:")
        print("  - Compresses PDF to under 20MB for web upload")
        print("  - Preserves all text and financial data")
        print("  - Optimizes images and removes duplicates")
        print("  - Shows compression statistics")
        print()
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"❌ Error: File not found: {input_file}")
        sys.exit(1)
    
    # Determine output file
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        # Auto-generate output filename
        path = Path(input_file)
        output_file = str(path.parent / f"{path.stem}_compressed{path.suffix}")
    
    # Check if output file already exists
    if os.path.exists(output_file):
        response = input(f"⚠️  {output_file} already exists. Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("❌ Cancelled")
            sys.exit(0)
    
    print("=" * 60)
    print("  PDF Compression Tool")
    print("=" * 60)
    print()
    print(f"📄 Input:  {input_file}")
    print(f"💾 Output: {output_file}")
    print()
    
    # Get original file size
    original_size = os.path.getsize(input_file) / (1024 * 1024)
    print(f"📊 Original size: {format_size(original_size)}")
    print()
    
    # Create compressor targeting 18MB (safely under 20MB)
    compressor = PDFCompressor(target_size_mb=18.0)
    
    print("🔄 Compressing PDF...")
    print("   This may take 10-60 seconds depending on file size...")
    print()
    
    try:
        # Compress with smart quality selection
        result_path, orig_size, comp_size, quality = compressor.smart_compress(
            input_file
        )
        
        # Move result to desired output location
        import shutil
        shutil.move(result_path, output_file)
        
        # Calculate reduction
        reduction = ((orig_size - comp_size) / orig_size * 100) if orig_size > comp_size else 0
        
        print("✅ Compression complete!")
        print()
        print("=" * 60)
        print("  Results")
        print("=" * 60)
        print(f"📊 Original size:   {format_size(orig_size)}")
        print(f"📊 Compressed size: {format_size(comp_size)}")
        print(f"📊 Size reduction:  {reduction:.1f}%")
        print(f"⚙️  Quality level:   {quality.upper()}")
        print()
        
        # Success message
        if comp_size <= 20:
            print("🎉 SUCCESS! File is now under 20MB and ready for upload!")
            print()
            print("Next steps:")
            print("  1. Open the web app (streamlit run app.py)")
            print(f"  2. Upload the compressed file: {output_file}")
            print("  3. Run your analysis!")
        elif comp_size <= 50:
            print("⚠️  File is now {format_size(comp_size)}")
            print("   This may still have upload issues (browser WebSocket limit)")
            print()
            print("Recommendations:")
            print("  1. Try uploading - it might work")
            print("  2. Or use 'Browse Files on Server' option:")
            print(f"     cp {output_file} /workspaces/Quality-Management-Check/pdf_uploads/")
        else:
            print(f"⚠️  File is still large: {format_size(comp_size)}")
            print()
            print("Recommendations:")
            print("  1. Use 'Browse Files on Server' option:")
            print(f"     cp {output_file} /workspaces/Quality-Management-Check/pdf_uploads/")
            print("  2. Or split PDF into smaller files")
        
        print()
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error during compression: {str(e)}")
        print()
        print("Possible solutions:")
        print("  1. Check if PDF is corrupted")
        print("  2. Try removing password protection")
        print("  3. Use 'Browse Files on Server' with original file")
        print("  4. Contact support with error details")
        sys.exit(1)

if __name__ == "__main__":
    main()
