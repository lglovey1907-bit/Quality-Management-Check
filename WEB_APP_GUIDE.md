# Web Application Guide

## 🌐 Running the Quality Management Analysis Web App

This guide explains how to run the browser-based interface for quality management analysis.

## Prerequisites

1. **Python 3.9+** installed
2. **Dependencies installed** (see Installation section)
3. **OpenAI API Key** configured in `.env` file

## Installation

```bash
# Install all dependencies including Streamlit
pip install -r requirements.txt
```

## Running the Web App

```bash
# From the project root directory
streamlit run app.py
```

The app will automatically open in your default browser at `http://localhost:8501`

## Features

### 1. **Dual Mode Analysis**
   - **📄 PDF Upload Mode**: Upload annual report PDFs for AI-powered extraction
   - **🌐 Online Mode**: Automatically fetch data from Yahoo Finance/Screener.in

### 2. **PDF Upload Mode**
   - Upload single PDF (containing multiple years)
   - Upload multiple PDFs (one per year)
   - AI extracts financial data automatically
   - Supports any PDF format annual report

### 3. **Online Mode**
   - Enter company ticker (e.g., RELIANCE, TCS, AAPL)
   - Select market (India, US, Global)
   - Automatic data fetching from multiple sources

### 4. **Interactive Results**
   - Visual score display with color coding
   - Category breakdown with progress bars
   - Key strengths highlighted
   - Red flags and concerns
   - Executive summary (AI-generated)

### 5. **Export Options**
   - Download report as JSON
   - Print-friendly format

## Usage Guide

### PDF Analysis Workflow

1. **Launch the app**:
   ```bash
   streamlit run app.py
   ```

2. **Select PDF Upload mode** in the sidebar

3. **Enter company details**:
   - Company Name (required)
   - Years to analyze (1-10)

4. **Upload PDFs**:
   - Choose upload mode (single or multiple)
   - Click "Browse files" or drag & drop
   - Supported format: PDF only

5. **Click "Analyze Quality"**

6. **View Results**:
   - Overall quality score
   - Category breakdown
   - Strengths and red flags
   - Detailed metrics

7. **Export** (optional):
   - Download as JSON
   - Share or save for records

### Online Analysis Workflow

1. **Launch the app**:
   ```bash
   streamlit run app.py
   ```

2. **Select Online Data Fetch mode** in sidebar

3. **Enter company details**:
   - Company ticker/name
   - Years to analyze
   - Market selection

4. **Click "Analyze Quality"**

5. **View and export results**

## Customization

### Changing Default Settings

Edit `app.py` to customize:

```python
# Change default years
value=5  # Change to your preferred default

# Change page layout
layout="wide"  # Options: "centered", "wide"

# Modify scoring thresholds
if score >= 7.5:  # Excellent threshold
    color = "green"
```

### Adding Custom Metrics

To add custom metrics to the display:

```python
# In display_report() function
st.markdown(f"**Custom Metric:** {report.custom_value}")
```

## Troubleshooting

### Issue: "OpenAI API Key not configured"
**Solution**: Set your API key in `.env` file:
```bash
OPENAI_API_KEY=sk-your-actual-key-here
```

### Issue: "Module not found: streamlit"
**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### Issue: PDF upload fails or "AxiosError: Network Error"
**Solution**: 
- **File size limit**: Keep PDFs under 200MB per file (500MB configured max)
- **Compress large PDFs**: Use https://www.ilovepdf.com/compress_pdf
- **Check file format**: Ensure PDF is not encrypted/password-protected
- **Check file content**: PDF must contain text (not just scanned images)
- **Browser issues**: Try clearing cache or different browser
- **Alternative**: Use command-line mode instead:
  ```bash
  python main.py --pdf-file report.pdf --company "Name"
  ```

📚 **Detailed troubleshooting guide:** See [TROUBLESHOOTING_UPLOAD.md](TROUBLESHOOTING_UPLOAD.md)

**Configuration:** Upload limits can be adjusted in `.streamlit/config.toml`:
```toml
[server]
maxUploadSize = 500  # In MB
```

### Issue: Analysis takes too long
**Solution**: 
- Check internet connection (for online mode)
- Reduce years to analyze
- Use smaller PDF files

### Issue: Port already in use
**Solution**: Run on different port:
```bash
streamlit run app.py --server.port 8502
```

## Advanced Configuration

### Run on Different Port

```bash
streamlit run app.py --server.port 8080
```

### Run with Custom Browser

```bash
streamlit run app.py --browser.serverAddress localhost
```

### Enable Development Mode

```bash
streamlit run app.py --server.runOnSave true
```

### Disable Auto-Open Browser

```bash
streamlit run app.py --server.headless true
```

## Deployment

### Deploy to Streamlit Cloud (Free)

1. Push code to GitHub
2. Visit [streamlit.io/cloud](https://streamlit.io/cloud)
3. Connect your repository
4. Add secrets (OPENAI_API_KEY) in Streamlit Cloud dashboard
5. Deploy!

### Deploy to Heroku

```bash
# Create Procfile
echo "web: streamlit run app.py --server.port=$PORT" > Procfile

# Deploy
heroku create your-app-name
git push heroku main
```

### Deploy with Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## Security Notes

⚠️ **Important Security Considerations:**

1. **Never commit `.env` file** to version control
2. **Use environment variables** for production deployments
3. **Implement authentication** for public deployments
4. **Rate limit API calls** to prevent abuse
5. **Validate file uploads** for security

## Performance Tips

1. **Cache results**: Streamlit automatically caches function results
2. **Optimize PDF size**: Compress PDFs before upload
3. **Limit years**: Analyzing 3-5 years is usually sufficient
4. **Use online mode** for quick checks (faster than PDF)

## Support

For issues or questions:
1. Check this guide first
2. Review main README.md
3. Check error messages in the app
4. Verify API keys are correctly set

## Examples

### Example 1: Analyze Reliance Industries (PDF)
1. Download annual report from [Reliance Investor Relations](https://www.ril.com/InvestorRelations/AnnualReport.aspx)
2. Select "PDF Upload" mode
3. Enter "Reliance Industries" as company name
4. Upload downloaded PDF
5. Click "Analyze Quality"

### Example 2: Analyze Apple (Online)
1. Select "Online Data Fetch" mode
2. Enter "AAPL" as ticker
3. Select "us" market
4. Set years to 5
5. Click "Analyze Quality"

### Example 3: Multi-Year PDF Analysis
1. Download 3 years of annual reports
2. Select "Multiple PDFs (One per Year)"
3. Upload all 3 PDFs
4. Analyze!

## Future Enhancements

Planned features:
- [ ] Peer comparison
- [ ] Historical trend charts
- [ ] PDF report generation
- [ ] Email notifications
- [ ] Batch analysis
- [ ] Custom scoring weights

---

**Enjoy analyzing with the web interface! 🚀**
