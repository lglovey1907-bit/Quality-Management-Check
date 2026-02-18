# Troubleshooting PDF Upload Errors

## Common Error: AxiosError: Network Error

This error typically occurs when uploading PDF files in the Streamlit web app. Here are solutions:

### 🔴 CRITICAL: Known Issue with Files > 20MB

**Problem:** Files around 20-25 MB can fail even though they're under the 200MB limit
**Symptom:** 16 MB works fine, but 21 MB and 25 MB fail with network error

**Root Cause:** Browser websocket message size limits, not file size limits

**BEST SOLUTION - Use Direct Analysis Script:**
```bash
python analyze_pdf_direct.py report.pdf "Company Name"

# For multiple files:
python analyze_pdf_direct.py report1.pdf report2.pdf report3.pdf "Company Name"
```

This completely bypasses the web upload and works reliably with any size file.

### Solution 1: Check File Size

**Problem:** File is too large for upload
**Fix:**

1. Check your PDF file size:
   - Right-click the PDF → Properties (Windows) or Get Info (Mac)
   - Size should be **under 200MB per file**

2. If file is too large, compress it:
   
   **Option A - Online Tools:**
   - Use https://www.ilovepdf.com/compress_pdf
   - Or https://smallpdf.com/compress-pdf
   
   **Option B - Adobe Acrobat:**
   - File → Save As Other → Reduced Size PDF
   
   **Option C - Command Line (Linux/Mac):**
   ```bash
   # Install ghostscript
   brew install ghostscript  # Mac
   sudo apt-get install ghostscript  # Linux
   
   # Compress PDF
   gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook \
      -dNOPAUSE -dQUIET -dBATCH \
      -sOutputFile=compressed.pdf input.pdf
   ```

### Solution 2: Clear Browser Cache

**Problem:** Browser cache causing upload issues
**Fix:**

1. **Chrome/Edge:**
   - Press `Ctrl+Shift+Delete` (Windows) or `Cmd+Shift+Delete` (Mac)
   - Select "Cached images and files"
   - Click "Clear data"
   - Refresh the page

2. **Firefox:**
   - Press `Ctrl+Shift+Delete`
   - Select "Cache"
   - Click "Clear Now"

3. **Or hard refresh:**
   - Press `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)

### Solution 3: Increase Upload Limits

**Problem:** Default limits too low
**Fix:**

The `.streamlit/config.toml` file has been pre-configured with higher limits:
- Max upload: 500MB
- Max message: 500MB

If you need even higher limits:

1. Edit `.streamlit/config.toml`:
   ```toml
   [server]
   maxUploadSize = 1000  # 1GB
   maxMessageSize = 1000
   ```

2. Restart the app:
   ```bash
   # Stop with Ctrl+C
   # Start again
   streamlit run app.py
   ```

### Solution 4: Use Command Line Instead

**Problem:** Web upload not working
**Fix:** Use CLI mode instead:

```bash
# Single PDF
python main.py --pdf-file report.pdf --company "Company Name" --years 5

# Multiple PDFs
python main.py --pdf-files report1.pdf report2.pdf --company "Company"
```

### Solution 5: Check Network Connection

**Problem:** Slow or unstable internet
**Fix:**

1. Check internet speed:
   - Visit https://fast.com
   - Should be at least 5 Mbps upload speed

2. Try wired connection instead of Wi-Fi

3. Disable VPN if active (can slow uploads)

4. Close other applications using bandwidth

### Solution 6: Run Locally (No Network Needed)

**Problem:** Network issues with external services
**Fix:**

1. Ensure you're running locally:
   ```bash
   streamlit run app.py
   ```

2. Access via `http://localhost:8501` (not external IP)

3. Check if firewall is blocking:
   - Windows: Settings → Firewall → Allow Python
   - Mac: System Preferences → Security → Allow Python

### Solution 7: Browser-Specific Issues

**Problem:** Browser compatibility
**Fix:**

Try a different browser:
- ✅ **Recommended:** Chrome, Edge, Firefox
- ⚠️ **May have issues:** Safari, Brave (disable shields)

Clear browser extensions:
- Disable ad blockers
- Disable privacy extensions
- Try incognito/private mode

### Solution 8: Memory Issues

**Problem:** System running out of memory
**Fix:**

1. Check available RAM:
   ```bash
   # Linux/Mac
   free -h
   
   # Windows
   tasklist /fi "imagename eq python.exe"
   ```

2. Close other applications

3. Restart your computer

4. For large files, use smaller PDFs or fewer years

### Solution 9: PDF Format Issues

**Problem:** PDF cannot be read
**Fix:**

Ensure PDF is valid:

1. **Check if password-protected:**
   - Open in PDF reader
   - Should not ask for password

2. **Check if scanned image:**
   - Try selecting text in the PDF
   - If you can't select text, it's a scanned image
   - Solution: Use OCR software first

3. **Re-save PDF:**
   - Open in Adobe Reader/Preview
   - File → Save As
   - Try uploading new file

### Solution 10: Restart Everything

**Problem:** Unknown issue
**Fix:**

Complete reset:

```bash
# 1. Stop Streamlit (Ctrl+C)

# 2. Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete

# 3. Restart Streamlit
streamlit run app.py
```

## Error Messages and Meanings

| Error Message | Meaning | Solution |
|---------------|---------|----------|
| `AxiosError: Network Error` | Upload failed | Solutions 1-3 |
| `File too large` | Exceeds size limit | Solution 1 |
| `Connection timeout` | Network slow | Solution 5 |
| `Error saving file` | Disk/permission issue | Check disk space |
| `Error during analysis` | API/processing error | Check API key |

## Still Not Working?

### Alternative: Use Command Line Interface

The CLI doesn't have upload limits and is more reliable:

```bash
# Direct analysis without upload UI
python main.py --pdf-file /path/to/report.pdf --company "ABC Corp"
```

### Alternative: Use Online Mode

If you don't need PDF upload:

```bash
# Automatically fetch data from Yahoo Finance
python main.py --company TICKER --years 5
```

### Check Logs

```bash
# Run with debug mode
streamlit run app.py --logger.level=debug
```

Check terminal output for detailed error messages.

## Performance Tips

1. **Optimize PDF size:**
   - Remove unnecessary images
   - Reduce resolution
   - Remove embedded fonts

2. **Limit analysis scope:**
   - Reduce years to 3-5 instead of 10
   - Focus on recent years

3. **Upload during off-peak:**
   - Late night/early morning
   - Less network congestion

4. **Use SSD storage:**
   - Faster file operations
   - Better for temp files

## Getting Help

If none of these solutions work:

1. **Check the terminal output** where you ran `streamlit run app.py`
2. **Note the exact error message**
3. **Try the command-line interface** as a workaround
4. **Check system requirements:**
   - Python 3.9+
   - 4GB+ RAM recommended
   - 1GB+ free disk space

## Prevention

To avoid future issues:

1. ✅ Keep PDFs under 50MB (compress larger files)
2. ✅ Use good internet connection
3. ✅ Close unnecessary applications
4. ✅ Keep browser updated
5. ✅ Regularly clear browser cache
6. ✅ Test with small files first

---

**Quick Fix Checklist:**
- [ ] File size < 200MB?
- [ ] Browser cache cleared?
- [ ] Internet connection stable?
- [ ] API key configured?
- [ ] PDF not password-protected?
- [ ] PDF contains text (not just images)?
- [ ] Tried different browser?
- [ ] Tried command-line instead?
