# How to Use Direct PDF Analysis (Step-by-Step)

## ⚠️ IMPORTANT: This is NOT for the Web Browser!

The `analyze_pdf_direct.py` script runs in your **terminal/command prompt**, not in the web browser.

---

## 📋 Step-by-Step Instructions

### Windows Users:

#### Step 1: Open Command Prompt
1. Press `Windows Key + R`
2. Type `cmd` and press Enter
3. Or search for "Command Prompt" in Start Menu

#### Step 2: Navigate to Your Project Folder
```cmd
cd C:\path\to\Quality-Management-Check
```

#### Step 3: Run the Analysis
```cmd
python analyze_pdf_direct.py path\to\your\file.pdf "Company Name"
```

**Example:**
```cmd
python analyze_pdf_direct.py C:\Users\YourName\Documents\annual_report.pdf "Reliance Industries"
```

---

### Mac/Linux Users:

#### Step 1: Open Terminal
- **Mac:** Press `Cmd + Space`, type "Terminal", press Enter
- **Linux:** Press `Ctrl + Alt + T`

#### Step 2: Navigate to Your Project Folder
```bash
cd /path/to/Quality-Management-Check
```

#### Step 3: Run the Analysis
```bash
python3 analyze_pdf_direct.py /path/to/your/file.pdf "Company Name"
```

**Example:**
```bash
python3 analyze_pdf_direct.py ~/Documents/annual_report.pdf "Reliance Industries"
```

---

## 🎯 Where Are Your PDF Files?

### Find Your PDF File Path:

**Windows:**
1. Right-click on your PDF file
2. Hold `Shift` and click "Copy as path"
3. Paste this path in the command

**Mac:**
1. Right-click (or Ctrl+click) on your PDF file
2. Hold `Option` key
3. Click "Copy [filename] as Pathname"
4. Paste this path in the command

**Linux:**
1. Right-click on your PDF file
2. Click "Properties"
3. Copy the location path
4. Add the filename to it

---

## 📝 Real Examples

### Example 1: Single PDF File

**Your files:**
- PDF: `C:\Users\John\Desktop\reliance_report_2024.pdf`
- Company: Reliance Industries

**Command:**
```cmd
cd C:\Users\John\Quality-Management-Check
python analyze_pdf_direct.py "C:\Users\John\Desktop\reliance_report_2024.pdf" "Reliance Industries"
```

### Example 2: Multiple PDF Files

**Your files:**
- PDF 1: `report_2024.pdf` (in same folder)
- PDF 2: `report_2023.pdf` (in same folder)
- PDF 3: `report_2022.pdf` (in same folder)
- Company: ABC Corporation

**Command:**
```cmd
cd C:\Users\John\Quality-Management-Check
python analyze_pdf_direct.py report_2024.pdf report_2023.pdf report_2022.pdf "ABC Corporation"
```

### Example 3: PDFs in Different Folder

**Your setup:**
- You're in: `C:\Users\John\Quality-Management-Check`
- PDFs are in: `C:\Users\John\Downloads\`

**Command:**
```cmd
cd C:\Users\John\Quality-Management-Check
python analyze_pdf_direct.py "C:\Users\John\Downloads\report1.pdf" "C:\Users\John\Downloads\report2.pdf" "Company Name"
```

---

## 🖱️ EASIER: Drag & Drop Method

### Windows:

1. **Create a shortcut:**
   - Right-click on `analyze_pdf.bat`
   - Click "Send to" → "Desktop (create shortcut)"

2. **Use it:**
   - Drag your PDF file(s) onto the desktop shortcut
   - A window will pop up asking for company name
   - Type the company name and press Enter
   - Done!

### Mac/Linux:

1. **Make script executable:**
   ```bash
   chmod +x analyze_pdf.sh
   ```

2. **Run it:**
   ```bash
   ./analyze_pdf.sh path/to/file.pdf "Company Name"
   ```

---

## ❓ What You'll See

After running the command, you'll see:

```
📄 annual_report_2024.pdf: 25.34MB

🏢 Company: Reliance Industries
📊 Analyzing 1 PDF file(s)...

🤖 Extracting data from annual_report_2024.pdf...

✅ Analysis complete!

══════════════════════════════════════════════════════════════
  QUALITY MANAGEMENT ANALYSIS REPORT
══════════════════════════════════════════════════════════════
  Company: Reliance Industries
  Analysis Date: 2026-02-15
  Years Analyzed: 5
══════════════════════════════════════════════════════════════

  OVERALL QUALITY SCORE: 7.5/10 [STRONG]
  
📊 CATEGORY SCORES
  Profitability & Margins         8.0  [Strong]
  Growth & Revenue Stability      7.5  [Strong]
  ...

💾 Save report to file? (y/n):
```

Type `y` and press Enter to save the results.

---

## 🆚 Comparison: Web vs Command Line

| Feature | Web Browser | Command Line (Direct) |
|---------|-------------|----------------------|
| **Where to run** | Browser at localhost:8501 | Terminal/Command Prompt |
| **File size** | ❌ Fails > 20MB | ✅ Any size |
| **How to start** | `streamlit run app.py` | `python analyze_pdf_direct.py` |
| **Upload files** | Click and upload | Specify file path |
| **For you** | ❌ Won't work (files > 20MB) | ✅ Perfect solution! |

---

## 🔧 Troubleshooting

### Error: "python is not recognized"

**Solution:**
- Windows: Use `py` instead of `python`
  ```cmd
  py analyze_pdf_direct.py file.pdf "Company"
  ```
- Or make sure Python is installed and in PATH

### Error: "No such file or directory"

**Solution:**
- Use the full path to your PDF file
- Or copy your PDF files to the project folder first
- Or `cd` to the folder containing your PDFs

### Error: "OPENAI_API_KEY not configured"

**Solution:**
- Make sure your `.env` file has your API key:
  ```
  OPENAI_API_KEY=sk-your-actual-key-here
  ```

---

## 🎬 Video Tutorial Alternative

If you're still confused, here's what to do:

### Option 1: Use VS Code Terminal (If you're in VS Code)
1. In VS Code, click "Terminal" menu → "New Terminal"
2. A terminal opens at the bottom of VS Code
3. Type the command there:
   ```bash
   python analyze_pdf_direct.py path/to/file.pdf "Company Name"
   ```

### Option 2: Copy PDFs to Project Folder (Easiest!)
1. Copy your PDF files to the `Quality-Management-Check` folder
2. Open terminal/command prompt in that folder
3. Run simple command:
   ```bash
   python analyze_pdf_direct.py your_file.pdf "Company Name"
   ```

---

## ✅ Quick Checklist

Before running the command:
- [ ] Terminal/Command Prompt is open
- [ ] You're in the `Quality-Management-Check` folder
- [ ] You know the path to your PDF file(s)
- [ ] You have the company name ready
- [ ] Your `.env` file has the OpenAI API key

Then run:
```bash
python analyze_pdf_direct.py "path/to/file.pdf" "Company Name"
```

---

## 🆘 Still Confused?

**SIMPLEST METHOD:**

1. **Copy your PDF files** to the `Quality-Management-Check` folder

2. **Open Command Prompt/Terminal** in that folder:
   - Windows: Type `cmd` in the folder's address bar
   - Mac: Right-click folder → "New Terminal at Folder"

3. **Run:**
   ```bash
   python analyze_pdf_direct.py filename.pdf "Your Company Name"
   ```

**That's it!** No web browser needed! 🎉

---

## 📞 Need More Help?

If you're still stuck, you can:
1. Check if Python is installed: `python --version`
2. Make sure you're in the right folder: `dir` (Windows) or `ls` (Mac/Linux)
3. List this project folder in the output above

The direct script is a **terminal/command-line tool**, not a web tool!
