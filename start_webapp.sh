#!/bin/bash

# Quality Management Analysis - Web App Launcher
# This script launches the Streamlit web application

echo "🚀 Starting Quality Management Analysis Web App..."
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "⚠️  Streamlit is not installed."
    echo "Installing Streamlit..."
    pip install streamlit
    echo ""
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env file from template..."
    cp .env.example .env 2>/dev/null || echo "OPENAI_API_KEY=your-openai-api-key-here" > .env
    echo "✅ .env file created. Please add your API keys before using PDF mode."
    echo ""
fi

# Check if OPENAI_API_KEY is set
source .env 2>/dev/null
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" == "your-openai-api-key-here" ]; then
    echo "⚠️  OPENAI_API_KEY not configured in .env file"
    echo "   PDF mode will not work without it."
    echo "   Online mode will work without API key."
    echo ""
fi

echo "📱 Opening web app in your browser..."
echo "   URL: http://localhost:8501"
echo ""
echo "   📝 Note: Upload limit set to 500MB (configurable in .streamlit/config.toml)"
echo "   💡 If you get upload errors, see TROUBLESHOOTING_UPLOAD.md"
echo ""
echo "   Press Ctrl+C to stop the server"
echo ""

# Launch Streamlit app
streamlit run app.py
