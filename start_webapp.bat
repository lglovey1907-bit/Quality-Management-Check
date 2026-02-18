@echo off
REM Quality Management Analysis - Web App Launcher (Windows)
REM This script launches the Streamlit web application

echo.
echo Starting Quality Management Analysis Web App...
echo.

REM Check if streamlit is installed
where streamlit >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Streamlit is not installed.
    echo Installing Streamlit...
    pip install streamlit
    echo.
)

REM Check if .env file exists
if not exist .env (
    echo .env file not found!
    echo Creating .env file from template...
    if exist .env.example (
        copy .env.example .env
    ) else (
        echo OPENAI_API_KEY=your-openai-api-key-here > .env
    )
    echo .env file created. Please add your API keys before using PDF mode.
    echo.
)

echo Opening web app in your browser...
echo URL: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

REM Launch Streamlit app
streamlit run app.py

pause
