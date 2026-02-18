# 🔧 Large PDF Upload Troubleshooting Guide

## ⚠️ Understanding the Upload Limitation

### The Problem

When uploading PDF files **larger than 20-30MB** through the web browser, you may encounter upload failures **BEFORE** the compression feature can even activate.

### Why This Happens

This is a **browser/WebSocket limitation**, not a Python or Streamlit limitation:

1. **Browser Upload Process**:
   - Browser reads your file
   - Encodes it for transfer
   - Sends via WebSocket to Streamlit server
   - **Limitation**: WebSocket message size limits (~20-30MB in most browsers)

2. **When Compression Runs**:
   - **AFTER** file successfully uploads to server
   - **NOT before** upload attempt

3. **The Catch-22**:
   - File > 20MB → Browser fails to upload
   - Compression code never gets to run
   - Even though compression is implemented, it can't help

---

## ✅ Solutions for Large Files

### Solution 1: Use "Browse Files on Server" (RECOMMENDED)

**Best for files > 20MB**

#### How It Works:
1. Copy PDF files to `pdf_uploads/` folder in project directory
2. Select "📁 Browse Files on Server" in web app
3. Choose files from dropdown
4. **No upload needed!** Files are already on server

#### Steps:
```bash
# 1. Copy your PDF to the uploads folder
cp /path/to/your/large_report.pdf /workspaces/Quality-Management-Check/pdf_uploads/

# 2. Start/refresh the web app
streamlit run app.py

# 3. In web app:
#    - Select "📁 Browse Files on Server"
#    - Choose your file from dropdown
#    - Click "Analyze"
```

#### Advantages:
✅ **No size limit** - Files of any size work
✅ **No browser restrictions** - Bypasses WebSocket limits
✅ **Faster** - No upload time
✅ **Reliable** - No network issues
✅ **Reusable** - Keep files for multiple analyses

---

### Solution 2: Pre-Compress PDF Before Upload

**For files 20-50MB that you want to upload**

#### Option A: Use External PDF Compressor

Free online tools:
- [ILovePDF](https://www.ilovepdf.com/compress_pdf) - Free, secure
- [SmallPDF](https://smallpdf.com/compress-pdf) - Free trial
- [PDF24](https://tools.pdf24.org/en/compress-pdf) - Free, no limits

#### Option B: Use Our Compression Script

If you have the project installed:

```bash
# Navigate to project
cd /workspaces/Quality-Management-Check

# Run compression script
python -c "
from src.pdf_compressor import PDFCompressor, format_size
compressor = PDFCompressor(target_size_mb=15.0)
output, orig, comp, quality = compressor.smart_compress('large_file.pdf', 'compressed_file.pdf')
print(f'Original: {format_size(orig)}')
print(f'Compressed: {format_size(comp)}')
print(f'Reduction: {((orig-comp)/orig*100):.1f}%')
"
```

#### Option C: Use a Standalone Tool

**Adobe Acrobat:**
1. Open PDF in Acrobat
2. File → Save As Other → Reduced Size PDF
3. Choose compatibility and save

**macOS Preview:**
1. Open PDF in Preview
2. File → Export
3. Quartz Filter → Reduce File Size
4. Save

**Windows:**
1. Use Microsoft Print to PDF
2. Choose "Print" from PDF viewer
3. Select "Microsoft Print to PDF"
4. This often reduces size

---

### Solution 3: Split Large PDF

**If file is > 100MB**

#### Why Split?
- Easier to upload
- Faster processing
- Better memory management
- Can analyze year-by-year

#### How to Split:

**Online Tools:**
- [iLovePDF Split](https://www.ilovepdf.com/split_pdf)
- [PDF2Go Split](https://www.pdf2go.com/split-pdf)

**Python Script:**
```python
from PyPDF2 import PdfReader, PdfWriter

def split_pdf(input_path, pages_per_file=50):
    reader = PdfReader(input_path)
    total_pages = len(reader.pages)
    
    part = 1
    for start_page in range(0, total_pages, pages_per_file):
        writer = PdfWriter()
        end_page = min(start_page + pages_per_file, total_pages)
        
        for page_num in range(start_page, end_page):
            writer.add_page(reader.pages[page_num])
        
        output_path = f"{input_path.replace('.pdf', '')}_part{part}.pdf"
        with open(output_path, 'wb') as out:
            writer.write(out)
        
        print(f"Created {output_path} ({end_page - start_page} pages)")
        part += 1

# Usage
split_pdf("large_annual_report.pdf", pages_per_file=100)
```

---

## 🎯 Which Solution to Use?

### Decision Tree

```
Is your file > 20MB?
│
├─ YES
│   │
│   ├─ Is file > 50MB?
│   │   │
│   │   ├─ YES → Use Solution 1: "Browse Files on Server"
│   │   │
│   │   └─ NO → Try Solution 2: Pre-compress, then upload
│   │
│   └─ Can you access server filesystem?
│       │
│       ├─ YES → Use Solution 1 (easiest!)
│       │
│       └─ NO → Use Solution 2 or 3
│
└─ NO (< 20MB)
    └─ Upload normally - auto-compression will handle it
```

### Quick Reference

| File Size | Best Solution | Alternative |
|-----------|---------------|-------------|
| < 20 MB | Direct upload | - |
| 20-50 MB | Pre-compress | Server browse |
| 50-100 MB | Server browse | Split + upload |
| > 100 MB | Server browse | Split or compress |

---

## 💡 Understanding Auto-Compression

### When It Works
✅ **AFTER** file successfully uploads to server
✅ For files that made it through browser upload
✅ Automatically processes files > 20MB
✅ Shows compression progress and results

### When It Doesn't Work
❌ **BEFORE** upload (can't compress what hasn't arrived)
❌ If browser fails upload due to WebSocket limits
❌ If file never reaches Python code

### How to Know It's Working

**Success scenario:**
```
📄 annual_report_2024.pdf - 35.2 MB
🎉 Large file uploaded successfully! Now compressing...
🔄 Compressing PDF for optimal processing...
✅ Compressed: 35.2 MB → 17.8 MB (49.4% reduction)
ℹ️ Quality level: MEDIUM
```

**Failure scenario (browser limit):**
```
[Upload button spinning indefinitely]
OR
[Upload fails with no file shown]
OR
[Browser shows "Connection lost" error]
```

---

## 🔍 Diagnosing Your Issue

### Test 1: Is It a Browser Limit?

Try uploading progressively smaller files:
- 10 MB → Works? Continue
- 15 MB → Works? Continue
- 20 MB → Works? Continue
- 25 MB → Fails? **Browser limit found**

### Test 2: Is It a Network Issue?

```bash
# Check your connection
ping localhost

# Restart Streamlit with verbose logging
streamlit run app.py --logger.level=debug
```

### Test 3: Is Compression Working for Uploaded Files?

Upload a file slightly > 20MB (like 22MB):
- If it uploads → You'll see compression messages
- If it fails → Browser limit hit, use server browse

---

## 📋 Step-by-Step: Using Server Browse

### For Single File Analysis

1. **Copy file to uploads folder:**
   ```bash
   cp ~/Downloads/annual_report_2024.pdf /workspaces/Quality-Management-Check/pdf_uploads/
   ```

2. **Open web app** (or refresh if already open)

3. **Select options:**
   - File Selection: "📁 Browse Files on Server"
   - Upload Mode: "Single PDF (Multiple Years)"

4. **Choose your file** from dropdown

5. **Click "🚀 Analyze Quality"**

### For Multiple Files

1. **Copy all files:**
   ```bash
   cp ~/Downloads/report_*.pdf /workspaces/Quality-Management-Check/pdf_uploads/
   ```

2. **In web app:**
   - Select "📁 Browse Files on Server"
   - Select "Multiple PDFs (One per Year)"
   - Check boxes for files to analyze

3. **Click "🚀 Analyze Quality"**

---

## ⚙️ Advanced Configuration

### Increase Browser Upload Tolerance

Edit `.streamlit/config.toml`:

```toml
[server]
maxUploadSize = 200  # Max 200MB (browser limits still apply)
maxMessageSize = 200
serverConnectionTimeoutSeconds = 300

[browser]
serverAddress = "localhost"
serverPort = 8501
```

**Note**: This helps but doesn't eliminate browser WebSocket limits.

### Use HTTP Instead of WebSocket

For very large files, consider using a different upload mechanism:

```bash
# Use a simple HTTP server
python -m http.server 8000 --directory pdf_uploads
```

Then access your files at `http://localhost:8000/`

---

## ❓ FAQ

### Q: Why can't you just fix the upload limit?
**A:** The limit is in the browser's WebSocket implementation, not our code. It's a security/stability feature of modern browsers.

### Q: Why does "Browse Files on Server" work?
**A:** It bypasses the browser upload entirely. The file is already on the server filesystem, so no WebSocket transfer needed.

### Q: Can I use this from another computer?
**A:** Yes, but you'll need to:
1. Copy files to the server's `pdf_uploads/` folder (via SCP, shared drive, etc.)
2. Access the Streamlit app via server IP address

### Q: Does compression still work with server browse?
**A:** No compression needed! Server browse has no size limits, so files are used as-is for analysis.

### Q: What about cloud deployments?
**A:** For cloud deployments (Heroku, AWS, etc.), use object storage (S3, Google Cloud Storage) and implement a file picker.

---

## 🚀 Quick Solutions Summary

**Problem**: Can't upload file > 20MB

**Solution 1** (Fastest): Copy to `pdf_uploads/`, use server browse
**Solution 2** (Portable): Compress PDF externally, then upload
**Solution 3** (Last resort): Split PDF into smaller files

**Remember**: Auto-compression works great for files that successfully upload. For files that fail at browser level, use server browse!

---

## 📞 Still Having Issues?

1. **Check file integrity**: Ensure PDF isn't corrupted
2. **Try different browser**: Chrome, Firefox, Safari have different limits
3. **Check server logs**: Look for error messages
4. **Clear browser cache**: Sometimes helps
5. **Use incognito mode**: Eliminates extension conflicts

**Last resort**: Use the command-line interface:
```bash
python main.py --pdf-file /path/to/large_report.pdf --company "Company Name"
```

This bypasses the web interface entirely and has no size limits!
