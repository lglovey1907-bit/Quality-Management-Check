# 🚀 Quick Start Guide

Welcome to the Quality Management Analysis AI Agent! This guide will get you up and running in minutes.

## Choose Your Interface

This tool offers **3 ways** to analyze companies:

| Method | Best For | Ease of Use | Features |
|--------|----------|-------------|----------|
| 🌐 **Web App** | Most users, beginners | ⭐⭐⭐⭐⭐ Easiest | Drag & drop, visual interface |
| 💻 **Command Line** | Quick analysis, automation | ⭐⭐⭐⭐ Easy | Fast, scriptable |
| 🐍 **Python API** | Developers, integration | ⭐⭐⭐ Moderate | Full control, customizable |

---

## 🌐 Option 1: Web Browser Interface (RECOMMENDED)

**The easiest way to get started!**

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure API Key (Required for PDF mode)
1. Open `.env` file
2. Replace `your-openai-api-key-here` with your actual OpenAI API key
3. Save the file

### Step 3: Launch Web App

**On Linux/Mac:**
```bash
chmod +x start_webapp.sh
./start_webapp.sh
```

**On Windows:**
```bash
start_webapp.bat
```

**Or manually:**
```bash
streamlit run app.py
```

### Step 4: Use the Web Interface

1. **Open your browser** at `http://localhost:8501`
2. **Choose mode**: PDF Upload or Online Fetch
3. **For PDF mode**:
   - Enter company name
   - Upload annual report PDF(s)
   - Click "Analyze Quality"
4. **For Online mode**:
   - Enter company ticker (e.g., RELIANCE, AAPL)
   - Select market and years
   - Click "Analyze Quality"
5. **View results** with visual charts and scores
6. **Download report** as JSON if needed

**That's it!** 🎉

---

## 💻 Option 2: Command Line Interface

Perfect for quick analysis or scripting.

### Interactive Mode

**Online analysis:**
```bash
python main.py
```

**PDF analysis:**
```bash
python main.py --pdf
```

Follow the prompts to enter company details.

### Direct Commands

**Analyze a public company:**
```bash
# Indian company
python main.py --company RELIANCE --years 5 --market india

# US company
python main.py --company AAPL --years 3 --market us
```

**Analyze from PDF:**
```bash
# Single PDF file
python main.py --pdf-file report.pdf --company "ABC Corp" --years 5

# Multiple PDF files
python main.py --pdf-files report1.pdf report2.pdf report3.pdf --company "ABC Corp"
```

**⚠️ PDF Upload Issues? Use Direct Analysis:**

If you get "AxiosError: Network Error" when uploading PDFs > 20MB in web interface:

```bash
# Direct analysis script (bypasses web upload - most reliable!)
python analyze_pdf_direct.py report.pdf "Company Name"

# Multiple PDFs:
python analyze_pdf_direct.py report1.pdf report2.pdf report3.pdf "Company Name"
```

This script:
- ✅ Works with files of any size (no 20MB browser limit)
- ✅ More reliable than web upload
- ✅ Shows progress and detailed errors
- ✅ Can save results to JSON
- ✅ No browser/network issues

# Multiple PDF files
python main.py --pdf-files report1.pdf report2.pdf report3.pdf --company "XYZ Ltd"
```

**Save results:**
```bash
python main.py --company TCS --save --output reports/tcs_analysis.json
```

---

## 🐍 Option 3: Python API

For developers who want to integrate the analysis into their own applications.

### Basic Usage

```python
from src import QualityManagementAgent

# Initialize agent
agent = QualityManagementAgent(use_ai=True)

# Analyze a company (online mode)
report = agent.analyze_company(
    company_identifier="RELIANCE",
    years=5,
    market="india"
)

# Print results
print(f"Quality Score: {report.overall_score}/10")
print(f"Strengths: {report.key_strengths}")
print(f"Red Flags: {report.red_flags}")
```

### PDF Analysis

```python
from src import QualityManagementAgent

# Initialize in PDF mode
agent = QualityManagementAgent(use_ai=True, pdf_mode=True)

# Analyze from PDF
report = agent.analyze_from_pdf(
    pdf_path="annual_report.pdf",
    company_name="Company Name",
    years=5
)

print(f"Score: {report.overall_score}/10")
```

See [README.md](README.md) for more examples.

---

## 📋 What You Need

### Required
- ✅ Python 3.9 or higher
- ✅ Internet connection (for online mode or API calls)

### Optional (but recommended)
- 🔑 OpenAI API Key - Required for:
  - PDF data extraction
  - AI-enhanced analysis
  - Executive summaries
- 🔑 FMP API Key - Optional for additional data sources

### Getting API Keys

**OpenAI API Key** (for PDF mode):
1. Visit https://platform.openai.com/api-keys
2. Sign up or log in
3. Create new API key
4. Copy and paste into `.env` file

**Financial Modeling Prep API Key** (optional):
1. Visit https://financialmodelingprep.com/developer/docs/
2. Sign up for free tier
3. Get your API key
4. Add to `.env` file

---

## 📊 Example: Analyze Your First Company

### Using Web App (Easiest)

1. Launch: `streamlit run app.py`
2. Select "Online Data Fetch"
3. Enter: `RELIANCE`
4. Click: "Analyze Quality"
5. Done! ✨

### Using Command Line

```bash
python main.py --company RELIANCE --years 5 --market india
```

### Expected Output

```
🔍 Searching for: RELIANCE
Found: Reliance Industries Ltd (RELIANCE)
✓ Data fetched from Yahoo Finance
✓ Analysis complete

══════════════════════════════════════════════════════════════════════
  QUALITY MANAGEMENT ANALYSIS REPORT
══════════════════════════════════════════════════════════════════════

  OVERALL QUALITY SCORE: 5.5/10 [MODERATE]

📊 CATEGORY SCORES
  Profitability & Margins         5.0  [Moderate]
  Growth & Revenue Stability      6.0  [Good]
  Financial Health & Leverage     5.0  [Moderate]
  ...
```

---

## 🆘 Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### "OpenAI API key not configured" (for PDF mode)
1. Edit `.env` file
2. Add your actual API key
3. Save and restart

### Company not found (online mode)
- Try different ticker format (e.g., `TCS.NS` instead of `TCS`)
- Check spelling
- Use PDF mode as alternative

### PDF extraction fails
- Ensure PDF contains extractable text (not scanned images)
- Check PDF is not password-protected
- Try smaller PDF files first

### Web app won't start
```bash
# Install Streamlit
pip install streamlit

# Check port is available
streamlit run app.py --server.port 8502
```

---

## 📚 Next Steps

- ✅ Try analyzing a company
- 📖 Read [WEB_APP_GUIDE.md](WEB_APP_GUIDE.md) for detailed web app features
- 📖 Read [README.md](README.md) for complete documentation
- 🔧 Customize scoring weights in `src/analyzer.py`
- 🌐 Deploy web app to Streamlit Cloud (free!)

---

## 🎯 Quick Reference

### Web App
```bash
streamlit run app.py
```

### Command Line - Online
```bash
python main.py --company TICKER --years N
```

### Command Line - PDF
```bash
python main.py --pdf-file report.pdf --company "Name"
```

### Python API
```python
from src import QualityManagementAgent
agent = QualityManagementAgent()
report = agent.analyze_company("TICKER")
```

---

**Happy Analyzing! 📊✨**

For detailed documentation, see [README.md](README.md)  
For web app help, see [WEB_APP_GUIDE.md](WEB_APP_GUIDE.md)
