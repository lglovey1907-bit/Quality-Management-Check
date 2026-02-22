#!/bin/bash

echo "🚀 Deploying cache fix for TCS company name issue..."

cd /workspaces/Quality-Management-Check

# Stage all changes
git add app.py CLEAR_CACHE_INSTRUCTIONS.md INDIAN_STOCKS_FIX_ANALYSIS.md deploy_indian_stocks_fix.sh

# Show what we're committing
echo ""
echo "📝 Files to commit:"
git status --short

echo ""
read -p "Continue with commit? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "❌ Aborted"
    exit 1
fi

# Commit
git commit -m "fix: Force reload data_fetcher module to clear Python cache

PROBLEM: TCS still showing as 'TCS' instead of 'Tata Consultancy Services Limited'
ROOT CAUSE: Python module import caching preventing new code from loading

FIXES:
- Added importlib.reload() to force fresh module load on each validation
- Added DEBUG output to see what validation returns
- Added 'Clear Cache' button for easy troubleshooting
- Created comprehensive troubleshooting guide

This ensures the hardcoded Indian stock mappings are loaded fresh each time."

# Push to remote
echo ""
echo "📤 Pushing to GitHub..."
git push origin main

echo ""
echo "✅ Changes pushed successfully!"
echo ""
echo "🔄 IMPORTANT NEXT STEPS:"
echo "1. Wait 1-2 minutes for Streamlit Cloud to redeploy"
echo "2. Go to: https://cmqcnehmat.streamlit.app/"
echo "3. HARD REFRESH: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)"
echo "4. Click the '🔄 Clear Cache' button in the app"
echo "5. Test with 'TCS' - should see DEBUG output with full name"
echo ""
echo "📖 See CLEAR_CACHE_INSTRUCTIONS.md for detailed steps"
