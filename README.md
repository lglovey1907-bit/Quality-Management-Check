# Quality Management Analysis AI Agent

An AI-powered agent that analyzes companies' quality management through comprehensive financial data analysis. The agent supports **two modes**: online data fetching from financial APIs (Screener.in, Yahoo Finance, Financial Modeling Prep) or **AI-powered PDF extraction** from uploaded annual reports. It provides detailed quality assessment reports with scoring, strengths, and red flag predictions.

## 🚀 Quick Start

**New to this project? Start here:**

1. **Install:** `pip install -r requirements.txt`
2. **Launch Web App:** `streamlit run app.py` (opens in browser)
3. **Upload PDF or enter ticker** and analyze!

👉 See [QUICK_START.md](QUICK_START.md) for detailed getting started guide

---

## Features

### 📊 Dual Data Input Modes

**Online Mode:**
- **Multiple Data Sources**: Automatically fetches data from Screener.in (Indian stocks), Yahoo Finance (Global), and Financial Modeling Prep API
- **Auto-detection**: Automatically selects the best data source based on company/market
- **Real-time Data**: Gets latest financial information

**PDF Mode (NEW):**
- **Upload Annual Reports**: Extract data directly from PDF annual reports
- **AI-Powered Extraction**: Uses OpenAI GPT-4 to intelligently parse unstructured financial data
- **Multi-year Support**: Process single PDF with multiple years or multiple PDFs (one per year)
- **Works Offline**: No need for internet access to financial APIs

Both modes support:
- **Multi-year Analysis**: Analyze 1-10 years of financial data
- **Comprehensive Metrics**: Revenue, profits, cash flows, assets, liabilities, ratios

### 📈 Quality Analysis
The agent evaluates companies across 7 key dimensions:

| Category | Weight | What's Analyzed |
|----------|--------|-----------------|
| Profitability & Margins | 20% | Operating margin, net margin, ROE trends |
| Growth & Revenue Stability | 15% | Revenue CAGR, profit growth, consistency |
| Financial Health & Leverage | 20% | Debt-to-equity, interest coverage, liquidity |
| Cash Flow Management | 15% | Operating cash flow, FCF, cash conversion |
| Capital Efficiency & Returns | 15% | ROCE, ROA, asset turnover |
| Quality of Earnings | 10% | Accruals analysis, earnings stability |
| Management & Governance | 5% | Dividend policy, capital allocation |

### 🎯 Output Report Includes
- **Overall Quality Score**: 0-10 scale with rating (Weak/Moderate/Strong)
- **Category-wise Scores**: Detailed breakdown by each quality dimension
- **Key Strengths**: Top positive factors identified in the analysis
- **Red Flags & Concerns**: Critical issues with severity ratings and recommendations
- **Executive Summary**: AI-generated comprehensive summary
- **Investment Thesis**: Bull case and key risks
- **Risk Assessment**: Material risks and their implications

### 📄 NEW: Institutional PDF Reports
Generate professional, institutional-grade PDF reports with:
- ✅ **Strategic Alignment Analysis**
- ✅ **Capital Allocation Discipline Assessment**
- ✅ **Governance Quality Evaluation**
- ✅ **Execution vs Narrative Gap Analysis**
- ✅ **Comprehensive Red Flags Section** (categorized by severity)
- ✅ **Quantitative Scoring Breakdown** with detailed methodology
- ✅ **Final Rating & Investment Perspective**
- ✅ **Professional formatting** ready for stakeholder presentations

### 📊 NEW: Enhanced Analytics Dashboard
Interactive visualizations powered by Plotly:
- **📊 Scorecard View**: Traditional metrics with color-coded ratings
- **📈 Interactive Charts**:
  - Radar Chart for pattern recognition
  - Horizontal Bar Chart for category comparison
  - Gauge Chart for overall score visualization
- **🎯 Red Flag Dashboard**:
  - Severity metrics (High/Medium/Low)
  - Category distribution pie chart
  - Detailed expandable analysis
- **Real-time Interactivity**: Hover tooltips, zoom, and pan

👉 See [PDF_DASHBOARD_GUIDE.md](PDF_DASHBOARD_GUIDE.md) for complete documentation

### 🗜️ NEW: Automatic PDF Compression
Smart compression for seamless uploads:
- **Auto-Detects**: Files > 20MB automatically compressed
- **Smart Quality**: Chooses optimal compression level (High → Medium → Low)
- **Fast Processing**: 5-30 seconds typical compression time
- **Preserves Data**: 100% text/table accuracy, optimized images only
- **Progress Feedback**: Real-time compression status and results
- **40-70% Reduction**: Typical file size savings
- **Fallback Safe**: Uses original file if compression fails

👉 See [PDF_COMPRESSION_GUIDE.md](PDF_COMPRESSION_GUIDE.md) for complete documentation

## Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Setup

1. **Clone the repository**
```bash
cd /workspaces/Quality-Management-Check
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Install PDF & Dashboard Features (NEW)**
```bash
# Linux/Mac
bash install_pdf_dashboard.sh

# Windows or alternative
python install_pdf_dashboard.py

# Or manually
pip install reportlab matplotlib plotly kaleido
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

### Required API Keys

| API Key | Required | Purpose |
|---------|----------|---------|
| `OPENAI_API_KEY` | Optional | Enables AI-enhanced analysis (executive summaries, thesis generation) |
| `FMP_API_KEY` | Optional | Access to Financial Modeling Prep API for additional data |

The agent works without API keys but provides enhanced insights with them.

## Usage

The agent supports **two modes**:
1. **Online Mode** (default): Fetches data from Yahoo Finance/Screener.in
2. **PDF Mode**: Extracts data from uploaded PDF annual reports using AI

### Online Mode - Interactive
```bash
python main.py
```

This starts an interactive session where you:
1. Enter company name or ticker symbol
2. Specify number of years to analyze
3. View the comprehensive report
4. Optionally save the report

### Online Mode - Command Line

**Basic analysis:**
```bash
python main.py --company RELIANCE
```

**Specify years:**
```bash
python main.py --company AAPL --years 3
```

**Save report:**
```bash
python main.py --company TCS --save
```

**Output as JSON:**
```bash
python main.py --company INFY --json
```

### PDF Mode - Interactive
```bash
python main.py --pdf
```

This starts PDF upload mode where you:
1. Enter company name
2. Choose single or multiple PDF mode
3. Provide path(s) to PDF annual report(s)
4. AI extracts financial data from PDFs
5. View the comprehensive report

### PDF Mode - Command Line

**Single PDF with multi-year data:**
```bash
python main.py --pdf-file annual_report_2024.pdf --company "ABC Corporation" --years 5
```

**Multiple PDFs (one per year):**
```bash
python main.py --pdf-files report_2024.pdf report_2023.pdf report_2022.pdf --company "ABC Corporation"
```

**PDF mode with save:**
```bash
python main.py --pdf-file report.pdf --company "XYZ Ltd" --save
```

**Note:** PDF mode requires `OPENAI_API_KEY` to be set for AI-powered data extraction.

**Full options:**
```bash
python main.py --company MSFT --years 5 --market us --save --output reports/microsoft.json
```

### Command Line Arguments

| Argument | Short | Description |
|----------|-------|-------------|
| `--pdf` | | Enable PDF upload mode (interactive) |
| `--pdf-file` | | Path to single PDF annual report |
| `--pdf-files` | | Paths to multiple PDF reports (one per year) |
| `--company` | `-c` | Company name or ticker symbol (or name for PDF mode) |
| `--years` | `-y` | Number of years to analyze (default: 5) |
| `--market` | `-m` | Market preference: india, us, global, auto (default: auto) - Online mode only |
| `--save` | `-s` | Save report to file |
| `--output` | `-o` | Output file path |
| `--no-ai` | | Disable AI-enhanced analysis |
| `--json` | | Output as JSON |

### 🌐 Web Browser Interface (Recommended!)

For a more user-friendly experience, use the web-based interface:

```bash
streamlit run app.py
```

The web app will open in your browser at `http://localhost:8501` with:
- 📤 **Drag & Drop PDF Upload**: Easy file upload interface (files < 20MB)
- 📁 **Browse Server Files**: Select large PDFs (> 20MB) from local folder - **NO UPLOAD NEEDED!**
- 🎨 **Visual Results**: Interactive charts and color-coded scores
- 📊 **Real-time Analysis**: See results as they're generated
- 📄 **NEW: PDF Export**: Generate institutional-grade PDF reports
- 📈 **NEW: Enhanced Dashboard**: Interactive Plotly visualizations
- 🎯 **NEW: Red Flag Dashboard**: Severity-based risk analysis
- 🔄 **Dual Mode Support**: Switch between PDF and Online modes
- 📱 **Responsive Design**: Works on desktop and mobile

**Quick start:**
```bash
# Install all dependencies (including PDF & dashboard)
pip install -r requirements.txt

# Or use quick installer
bash install_pdf_dashboard.sh  # Linux/Mac
python install_pdf_dashboard.py  # Windows

# Launch the web app
streamlit run app.py
```

**⚠️ For Large PDF Files (> 20MB):**

Instead of uploading, use the "Browse Files on Server" option:

1. **Copy your PDFs** to the `pdf_uploads` folder in this project
2. **Refresh the web app** (F5)
3. **Select "📁 Browse Files on Server"** option
4. **Choose files from dropdown** - no upload, no size limits!

📖 **Detailed Guide:** [WEB_LARGE_PDF_SOLUTION.md](WEB_LARGE_PDF_SOLUTION.md)

See [WEB_APP_GUIDE.md](WEB_APP_GUIDE.md) for detailed web app documentation.

### Programmatic Usage

**Online Mode:**
```python
from src import QualityManagementAgent

# Initialize the agent
agent = QualityManagementAgent(use_ai=True)

# Analyze a company
report = agent.analyze_company(
    company_identifier="RELIANCE",
    years=5,
    market="india"
)

# Access report data
print(f"Overall Score: {report.overall_score}/10")
print(f"Key Strengths: {report.key_strengths}")
```

**PDF Mode:**
```python
from src import QualityManagementAgent

# Initialize in PDF mode
agent = QualityManagementAgent(use_ai=True, pdf_mode=True)

# Analyze from single PDF
report = agent.analyze_from_pdf(
    pdf_path="annual_report_2024.pdf",
    company_name="ABC Corporation",
    years=5
)

# Or use multiple PDFs
from src import parse_multiple_reports

fin_data = parse_multiple_reports(
    pdf_paths=["report_2024.pdf", "report_2023.pdf", "report_2022.pdf"],
    company_name="XYZ Ltd"
)
report = agent.analyzer.analyze(fin_data)
```

**Format and Save:**
```python
# Generate formatted output
from src import ReportFormatter
formatter = ReportFormatter()
formatter.print_report(report)
formatter.print_report(report)

# Save as JSON or Markdown
formatter.save_report(report, "report.json", format="json")
formatter.save_report(report, "report.md", format="markdown")
```

## Examples

### Example 1: Analyzing an Indian Company
```bash
python main.py --company RELIANCE --years 5
```

Output includes:
- Quality Score: 7.8/10 (Strong)
- Key strengths identified in profitability and cash management
- Red flags for high capex requirements

### Example 2: Analyzing a US Tech Company
```bash
python main.py --company AAPL --market us --years 3
```

### Example 3: Batch Analysis (Programmatic)
```python
from src import QualityManagementAgent

agent = QualityManagementAgent()
companies = ["TCS", "INFY", "WIPRO"]

for company in companies:
    report = agent.analyze_company(company, years=3)
    print(f"{company}: {report.overall_score}/10")
```

## Understanding the Report

### Quality Score Interpretation

| Score Range | Rating | Interpretation |
|-------------|--------|----------------|
| 8.0 - 10.0 | Excellent | High-quality company with strong fundamentals |
| 7.0 - 7.9 | Strong | Above-average quality, minor concerns |
| 5.0 - 6.9 | Moderate | Average quality, requires closer analysis |
| 3.0 - 4.9 | Fair | Below-average, significant concerns present |
| 0.0 - 2.9 | Weak | Poor quality, major red flags |

### Red Flag Severity Levels

- **High**: Critical issues requiring immediate attention
- **Medium**: Significant concerns to monitor
- **Low**: Minor issues for awareness

## Data Sources

### Screener.in (Indian Markets)
- Best for: BSE/NSE listed companies
- Data: P&L, Balance Sheet, Cash Flow, Ratios
- Coverage: 5000+ Indian companies

### Yahoo Finance (Global)
- Best for: US and international companies
- Data: Comprehensive financial statements
- Coverage: Major global exchanges

### Financial Modeling Prep (Premium)
- Best for: Deep US market data
- Requires: API key
- Coverage: NYSE, NASDAQ, additional metrics

## Project Structure

```
Quality-Management-Check/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── .env.example           # Environment template
├── README.md              # Documentation
├── src/
│   ├── __init__.py        # Package exports
│   ├── agent.py           # Main AI agent
│   ├── data_fetcher.py    # Data fetching module
│   ├── analyzer.py        # Quality analysis engine
│   └── report_generator.py # Report formatting
└── reports/               # Saved reports (created on save)
```

## 🌐 Deployment

### Streamlit Community Cloud (Recommended)

Deploy your app for free on Streamlit Community Cloud:

**Quick Deploy (5 minutes):**
1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add your OpenAI API key to secrets
5. Deploy!

Your app will be live at: `https://your-app-name.streamlit.app`

📖 **Full Guide:** [DEPLOYMENT.md](DEPLOYMENT.md) - Complete step-by-step deployment instructions

**Deployment files included:**
- ✅ `requirements.txt` - Python dependencies
- ✅ `packages.txt` - System dependencies  
- ✅ `.streamlit/config.toml` - Streamlit configuration
- ✅ `.streamlit/secrets.toml.example` - Secrets template

### Alternative Platforms

The app can also be deployed on:
- **Render** - Good for Python apps, free tier available
- **Railway** - Simple deployment, free tier available
- **Heroku** - Traditional option (requires buildpack)

**Note:** Streamlit Community Cloud is the recommended platform as it's specifically optimized for Streamlit apps.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

MIT License

## Disclaimer

This tool is for educational and research purposes only. The analysis provided should not be considered as financial advice. Always conduct your own research and consult with a qualified financial advisor before making investment decisions.