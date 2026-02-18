# Direct PDF Analysis - No Web Upload Required

## 🎯 Best Solution for Files > 20MB

If you're experiencing **"AxiosError: Network Error"** when uploading PDFs in the web interface, use this direct analysis method instead.

## Why Use This?

| Web Upload | Direct Analysis |
|------------|-----------------|
| ❌ Fails for files > 20MB | ✅ Works with any file size |
| ❌ Browser limits | ✅ No browser involved |
| ❌ Network errors | ✅ Direct file access |
| ⚠️ Can timeout | ✅ Reliable completion |

## 🚀 Quick Usage

### Method 1: Python Script (Recommended)

**Single PDF:**
```bash
python analyze_pdf_direct.py report.pdf "Company Name"
```

**Multiple PDFs:**
```bash
python analyze_pdf_direct.py report1.pdf report2.pdf report3.pdf "Company Name"
```

**Example:**
```bash
python analyze_pdf_direct.py annual_report_2024.pdf "Reliance Industries"
```

### Method 2: Drag & Drop Helper Scripts

**Windows:**
1. Drag your PDF file(s) onto `analyze_pdf.bat`
2. Enter company name when prompted
3. Done!

**Linux/Mac:**
```bash
chmod +x analyze_pdf.sh
./analyze_pdf.sh report.pdf "Company Name"
```

Or drag files onto the script in your file manager.

## 📋 Features

✅ **No size limits** - Analyze PDFs of any size  
✅ **Progress tracking** - See which file is being processed  
✅ **Error details** - Get detailed error messages if something fails  
✅ **Save option** - Automatically prompts to save results as JSON  
✅ **Same analysis** - Uses the exact same AI analysis as web app  
✅ **Faster** - No upload overhead, direct file access  

## 📊 Example Output

```
📄 annual_report_2024.pdf: 25.34MB
📄 annual_report_2023.pdf: 21.87MB

🏢 Company: ABC Corporation
📊 Analyzing 2 PDF file(s)...

🤖 Extracting data from 2 PDFs...

✅ Analysis complete!

══════════════════════════════════════════════════════════════
  QUALITY MANAGEMENT ANALYSIS REPORT
══════════════════════════════════════════════════════════════

  OVERALL QUALITY SCORE: 7.5/10 [STRONG]
  
📊 CATEGORY SCORES
  Profitability & Margins         8.0  [Strong]
  Growth & Revenue Stability      7.5  [Strong]
  ...

💾 Save report to file? (y/n): y
✅ Report saved to: ABC_Corporation_analysis_20260215.json
```

## 🔧 How It Works

1. **Reads PDF files directly** from your file system
2. **No web upload** - bypasses browser and network entirely
3. **Same AI extraction** - uses OpenAI GPT-4 to parse financial data
4. **Same analysis engine** - identical quality scoring as web app
5. **Displays results** in terminal with formatted output
6. **Optional save** - prompts to save results as JSON

## 💡 When to Use

Use direct analysis when:
- ✅ PDF file is larger than 20 MB
- ✅ Web upload keeps failing with network errors
- ✅ You have multiple large PDFs
- ✅ You prefer command-line tools
- ✅ You want faster, more reliable analysis
- ✅ You're automating analysis in scripts

Use web interface when:
- Files are small (< 15 MB)
- You prefer visual interface
- You want to see charts and graphs
- You need to quickly try different companies

## 🆘 Troubleshooting

### Error: "OPENAI_API_KEY not configured"
**Solution:**
```bash
# Edit .env file
nano .env

# Add your key:
OPENAI_API_KEY=sk-your-actual-key-here
```

### Error: "File not found"
**Solution:**
```bash
# Use full path to PDF:
python analyze_pdf_direct.py "/full/path/to/report.pdf" "Company"

# Or cd to the directory first:
cd /path/to/pdfs
python /path/to/Quality-Management-Check/analyze_pdf_direct.py report.pdf "Company"
```

### Error: "Module not found"
**Solution:**
```bash
# Install dependencies:
pip install -r requirements.txt
```

### The script is slow
**Expected behavior:**
- Large PDFs (20-50 MB) can take 1-3 minutes to extract
- AI processing takes 30-60 seconds per file
- Total time: 2-5 minutes for comprehensive analysis

This is normal! The script shows progress messages.

## 📁 File Requirements

Same as web upload:
- ✅ PDF format
- ✅ Contains extractable text (not scanned images)
- ✅ Not password-protected
- ✅ Valid PDF structure

But unlike web upload:
- ✅ **No file size limit!**
- ✅ Can handle very large annual reports
- ✅ Can process many files at once

## 🔄 Comparison: All PDF Analysis Methods

| Method | File Size Limit | Ease of Use | Reliability | Speed |
|--------|----------------|-------------|-------------|-------|
| **Web Upload** | ~20 MB | ⭐⭐⭐⭐⭐ Easiest | ⭐⭐⭐ Good | ⭐⭐⭐⭐ Fast |
| **Direct Analysis** | Unlimited | ⭐⭐⭐⭐ Easy | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐⭐ Fast |
| **CLI (main.py)** | Unlimited | ⭐⭐⭐ Moderate | ⭐⭐⭐⭐ Very Good | ⭐⭐⭐⭐ Fast |

## 💻 Advanced Usage

### Analyze Multiple Companies in Batch

Create a script:
```bash
#!/bin/bash

# analyze_batch.sh
python analyze_pdf_direct.py company1_report.pdf "Company One"
python analyze_pdf_direct.py company2_report.pdf "Company Two"
python analyze_pdf_direct.py company3_report.pdf "Company Three"
```

### Automate with Saving

```python
# auto_analyze.py
import subprocess
import sys

pdfs = [
    ("report1.pdf", "ABC Corp"),
    ("report2.pdf", "XYZ Ltd"),
]

for pdf, company in pdfs:
    print(f"\n{'='*60}")
    print(f"Analyzing {company}")
    print(f"{'='*60}\n")
    
    subprocess.run([
        sys.executable,
        "analyze_pdf_direct.py",
        pdf,
        company
    ])
```

### Integrate into Your Workflow

```python
from pathlib import Path
from src import QualityManagementAgent, parse_multiple_reports

# Get all PDFs in a directory
pdf_dir = Path("./annual_reports")
pdfs = list(pdf_dir.glob("*.pdf"))

agent = QualityManagementAgent(use_ai=True, pdf_mode=True)

for pdf in pdfs:
    company = pdf.stem.replace("_", " ")
    report = agent.analyze_from_pdf(str(pdf), company, years=5)
    print(f"{company}: {report.overall_score}/10")
```

## 📚 See Also

- [TROUBLESHOOTING_UPLOAD.md](TROUBLESHOOTING_UPLOAD.md) - Detailed troubleshooting
- [QUICK_START.md](QUICK_START.md) - Getting started guide
- [README.md](README.md) - Full documentation
- [WEB_APP_GUIDE.md](WEB_APP_GUIDE.md) - Web interface guide

## ✅ Summary

**For files > 20 MB or repeated upload errors:**

```bash
python analyze_pdf_direct.py your_file.pdf "Company Name"
```

**This is the most reliable method for large PDFs!** 🎯
