@echo off
REM Direct PDF Analysis - Windows Batch Script
REM Drag and drop your PDF files onto this script to analyze them

echo.
echo ========================================
echo   Quality Management PDF Analyzer
echo ========================================
echo.

REM Check if files were provided
if "%~1"=="" (
    echo ERROR: No files provided
    echo.
    echo USAGE:
    echo   1. Drag and drop PDF file(s) onto this script
    echo   2. Or run: analyze_pdf.bat "file.pdf" "Company Name"
    echo.
    pause
    exit /b 1
)

REM Collect all PDF files
set PDF_FILES=
set COUNT=0
:collect_files
if "%~1"=="" goto done_collecting
if /i "%~x1"==".pdf" (
    set PDF_FILES=%PDF_FILES% "%~1"
    set /a COUNT+=1
)
shift
goto collect_files

:done_collecting

if %COUNT%==0 (
    echo ERROR: No PDF files found
    pause
    exit /b 1
)

echo Found %COUNT% PDF file(s)
echo.

REM Ask for company name
set /p COMPANY_NAME="Enter company name: "

if "%COMPANY_NAME%"=="" (
    echo ERROR: Company name is required
    pause
    exit /b 1
)

echo.
echo Analyzing...
echo.

REM Run the direct analysis script
python analyze_pdf_direct.py %PDF_FILES% "%COMPANY_NAME%"

echo.
pause
