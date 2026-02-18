# Deploying to Streamlit Community Cloud

This guide will help you deploy your Pattern Pulse application to Streamlit Community Cloud for free!

## 🚀 Quick Deployment (5 minutes)

### Prerequisites
- ✅ GitHub account
- ✅ OpenAI API key (required for AI analysis)
- ✅ Your repository pushed to GitHub

### Step 1: Push Code to GitHub

If you haven't already, push your code to GitHub:

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR-USERNAME/Quality-Management-Check.git
git branch -M main
git push -u origin main
```

### Step 2: Sign Up for Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Authorize Streamlit to access your repositories

### Step 3: Deploy Your App

1. Click **"New app"** button
2. Fill in the deployment form:
   - **Repository**: Select `YOUR-USERNAME/Quality-Management-Check`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL** (optional): Choose a custom subdomain like `pattern-pulse`

3. Click **"Deploy!"**

### Step 4: Configure Secrets (API Keys)

1. While your app is deploying, click **"Advanced settings"** → **"Secrets"**
2. Copy the content from `.streamlit/secrets.toml.example`
3. Paste into the secrets editor
4. **Replace** placeholder values with your actual API keys:

```toml
# Required: OpenAI API Key (for AI analysis and PDF extraction)
OPENAI_API_KEY = "sk-your-actual-openai-key-here"

# Optional: Other API keys
# FMP_API_KEY = "your-fmp-key-if-you-have-one"
```

5. Click **"Save"**

### Step 5: Wait for Deployment

- Initial deployment takes 5-10 minutes
- You'll see logs in the deployment console
- Once complete, your app will be live at: `https://YOUR-APP-NAME.streamlit.app`

🎉 **Done!** Your app is now live and accessible to anyone with the URL.

---

## 📋 Deployment Files Overview

The following files are used by Streamlit Community Cloud:

### `requirements.txt`
Lists all Python packages needed by your app. Already configured with:
- Streamlit, OpenAI, Pandas, Plotly
- PDF processing (PyPDF2, pdfplumber)
- Report generation (reportlab, matplotlib)

### `packages.txt`
System-level dependencies (apt packages):
- `poppler-utils` - PDF processing
- `libjpeg-dev`, `zlib1g-dev` - Image processing
- `libfreetype6-dev` - Matplotlib rendering

### `.streamlit/config.toml`
Streamlit configuration:
- Upload size limit: 20MB
- Theme settings
- Server configuration

### `.streamlit/secrets.toml.example`
Template for API keys and secrets. **Never commit actual secrets!**

---

## 🔧 Updating Your Deployed App

### Automatic Updates
Every time you push to your main branch, Streamlit will automatically redeploy:

```bash
git add .
git commit -m "Update features"
git push origin main
```

Wait 1-2 minutes for automatic redeployment.

### Manual Reboot
From Streamlit Cloud dashboard:
1. Go to your app
2. Click ⋮ (three dots) menu
3. Select **"Reboot app"**

---

## 🔐 Managing Secrets

### Updating API Keys

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click on your app
3. Click **"Settings"** → **"Secrets"**
4. Update the values
5. Click **"Save"** (app will automatically restart)

### Security Best Practices

✅ **DO:**
- Use Streamlit secrets for all API keys
- Keep `.streamlit/secrets.toml` in `.gitignore`
- Use separate API keys for production vs development
- Monitor your OpenAI usage dashboard

❌ **DON'T:**
- Commit API keys to GitHub
- Share your secrets.toml file
- Use the same keys across multiple projects unmonitored

---

## 🐛 Troubleshooting

### App Won't Start

**Error: `ModuleNotFoundError`**
- **Cause**: Missing dependency in `requirements.txt`
- **Fix**: Add the missing package to `requirements.txt` and push

**Error: `FileNotFoundError`**
- **Cause**: App can't find required files
- **Fix**: Ensure all files are committed to GitHub

### Blank Page / White Screen

**Check logs:**
1. Go to app settings
2. Click **"Manage app"** → **"Logs"**
3. Look for error messages

**Common causes:**
- Missing `OPENAI_API_KEY` in secrets
- Syntax error in code
- Import errors

### PDF Upload Not Working

**Error: `File size exceeds limit`**
- **Cause**: File too large (>20MB)
- **Fix**: Users should use the built-in PDF compression tool

**Error: `PDF parsing failed`**
- **Cause**: Corrupted or encrypted PDF
- **Fix**: Ask users to ensure PDF is not password-protected

### Slow Performance

**Optimization tips:**
- Use caching: `@st.cache_data` decorator
- Limit API calls
- Optimize large data processing

**Resource limits (Free tier):**
- 1 GB RAM
- 1 CPU core
- Apps sleep after inactivity (wake up on first visit)

---

## 📊 Monitoring Your App

### View Analytics

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click your app
3. View metrics:
   - Visitors count
   - Error rate
   - CPU/Memory usage

### Check Logs

Real-time logs help debug issues:
```
streamlit.io → App Settings → Logs
```

### OpenAI Usage

Monitor your API usage:
1. Go to [platform.openai.com/usage](https://platform.openai.com/usage)
2. Set up budget alerts
3. Monitor daily spend

---

## 💰 Cost Considerations

### Streamlit Community Cloud
- **FREE** forever for public apps
- Unlimited usage
- Community support

### OpenAI API Costs
Your main cost is OpenAI API usage:

**Typical costs per analysis:**
- PDF extraction: ~$0.01 - $0.05
- Quality analysis: ~$0.02 - $0.08
- Report generation: ~$0.01 - $0.03

**Estimated:** $0.05 - $0.15 per complete analysis

**Budget recommendations:**
- Set OpenAI budget limit: $10-50/month
- Enable email alerts at 50% and 80%
- Monitor usage weekly

---

## 🚀 Performance Optimization

### Caching Strategies

Add caching to expensive operations:

```python
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data(company):
    # Expensive data loading
    return data
```

### Session State

Store data in session state to avoid recomputation:

```python
if 'report' not in st.session_state:
    st.session_state.report = None
```

### Lazy Loading

Load heavy dependencies only when needed:

```python
if st.button("Generate PDF"):
    from src import generate_institutional_pdf
    # Only import when actually needed
```

---

## 🔄 Backup & Version Control

### Regular Backups

```bash
# Tag important releases
git tag -a v1.0 -m "Stable release"
git push origin v1.0
```

### Rollback to Previous Version

If something breaks:

```bash
# Revert to previous commit
git revert HEAD
git push origin main
```

Or change branch in Streamlit settings to specific commit/tag.

---

## 📚 Additional Resources

### Streamlit Documentation
- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [Resource Limits](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app#resource-limits)

### Support
- [Streamlit Forum](https://discuss.streamlit.io/)
- [Streamlit Discord](https://discord.gg/streamlit)

### Your App Resources
- [README.md](README.md) - Full app documentation
- [WEB_APP_GUIDE.md](WEB_APP_GUIDE.md) - Web interface guide
- [PDF_DASHBOARD_GUIDE.md](PDF_DASHBOARD_GUIDE.md) - Dashboard features

---

## ✅ Deployment Checklist

Before going live, verify:

- [ ] All code committed and pushed to GitHub
- [ ] `requirements.txt` includes all dependencies
- [ ] `packages.txt` includes system dependencies
- [ ] `.streamlit/config.toml` configured properly
- [ ] API keys added to Streamlit secrets
- [ ] Tested app locally with `streamlit run app.py`
- [ ] Removed any hardcoded secrets from code
- [ ] `.gitignore` includes `.streamlit/secrets.toml`
- [ ] README.md updated with deployment link
- [ ] OpenAI budget limits set

---

## 🎯 Quick Reference

| Action | Command/Link |
|--------|--------------|
| Deploy new app | [share.streamlit.io](https://share.streamlit.io) |
| View logs | App settings → Logs |
| Update secrets | App settings → Secrets |
| Reboot app | ⋮ menu → Reboot app |
| Local test | `streamlit run app.py` |
| Check OpenAI usage | [platform.openai.com/usage](https://platform.openai.com/usage) |

---

**Need help?** Open an issue on GitHub or refer to [Streamlit Community Cloud Documentation](https://docs.streamlit.io/streamlit-community-cloud).
