#!/bin/bash

# Deploy the Indian stocks company name fix to Streamlit Cloud

echo "🚀 Deploying Indian stocks fix (TCS, RELIANCE, etc.)..."

cd /workspaces/Quality-Management-Check

# Stage changes  
git add src/data_fetcher.py app.py

# Show what we're committing
echo "📝 Changes to commit:"
git diff --cached --stat

# Commit
git commit -m "fix: Indian stocks now show full company names

- Prioritize hardcoded mapping for 48 major Indian stocks
- TCS now displays 'Tata Consultancy Services Limited'
- RELIANCE now displays 'Reliance Industries Limited'  
- Keep 'Limited' suffix (official part of Indian company names)
- Enhanced Yahoo Finance validation
- Fixes issue where only ticker was displayed"

# Push to remote
echo "🔄 Pushing to GitHub..."
git push origin main

echo ""
echo "✅ Changes pushed successfully!"
echo "🌐 Streamlit Cloud will automatically redeploy in 1-2 minutes"
echo "🔍 Check your app: https://cmqcnehmat.streamlit.app/"
echo ""
echo "💡 After deployment, clear browser cache (Ctrl+Shift+R) if you still see old data"
