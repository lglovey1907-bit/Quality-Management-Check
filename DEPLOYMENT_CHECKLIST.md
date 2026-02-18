# Pre-Deployment Checklist

Use this checklist before deploying to Streamlit Community Cloud:

## ✅ Required Files

- [ ] `requirements.txt` - All Python dependencies listed
- [ ] `packages.txt` - System dependencies (poppler-utils, etc.)
- [ ] `.streamlit/config.toml` - Streamlit configuration
- [ ] `.streamlit/secrets.toml.example` - Secrets template (example only)
- [ ] `.gitignore` - Secrets and sensitive files excluded
- [ ] `app.py` - Main Streamlit application file
- [ ] `README.md` - Documentation

## 🔐 Security

- [ ] No API keys in code (use secrets)
- [ ] `.streamlit/secrets.toml` is in `.gitignore`
- [ ] `.env` is in `.gitignore`
- [ ] No hardcoded credentials anywhere
- [ ] Secrets template (`.streamlit/secrets.toml.example`) has placeholder values only

## 🧪 Testing

- [ ] App runs locally: `streamlit run app.py`
- [ ] PDF upload works (files < 20MB)
- [ ] PDF compression tool link works
- [ ] Analysis completes successfully
- [ ] PDF report generation works
- [ ] No console errors

## 📦 Dependencies

- [ ] All imports are in `requirements.txt`
- [ ] System packages are in `packages.txt`
- [ ] Version numbers specified (e.g., `streamlit>=1.30.0`)
- [ ] No conflicting package versions

## 🔧 Configuration

- [ ] Upload size limit set to 20MB in `.streamlit/config.toml`
- [ ] Theme configured (optional)
- [ ] Page title and icon set in `app.py`

## 📝 GitHub Repository

- [ ] Code pushed to GitHub
- [ ] Repository is public (for free Streamlit Cloud)
- [ ] `main` branch exists
- [ ] All files committed
- [ ] `.git` directory exists

## 🚀 Streamlit Cloud Setup

- [ ] GitHub account connected to Streamlit Cloud
- [ ] Repository authorized for Streamlit access
- [ ] API keys ready to paste into secrets
- [ ] Custom subdomain chosen (optional)

## 📊 API Keys Ready

Copy these to Streamlit secrets (get from respective platforms):

- [ ] `OPENAI_API_KEY` - From [platform.openai.com](https://platform.openai.com/api-keys)
- [ ] `FMP_API_KEY` (optional) - From Financial Modeling Prep
- [ ] `ANTHROPIC_API_KEY` (optional) - From Anthropic

## 💰 Budget Setup

- [ ] OpenAI budget limit set (recommended: $10-50/month)
- [ ] Email alerts enabled at 50% and 80%
- [ ] Usage monitoring dashboard bookmarked

## 📚 Documentation

- [ ] README.md mentions deployed URL (update after deployment)
- [ ] DEPLOYMENT.md read through
- [ ] User guide links working

## 🎯 Post-Deployment

After deploying, verify:

- [ ] App loads without errors
- [ ] Secrets are working (no "API key missing" errors)
- [ ] PDF upload functional
- [ ] Analysis runs end-to-end
- [ ] Logs show no critical errors
- [ ] Share URL with test users

---

## Quick Commands

```bash
# Test locally
streamlit run app.py

# Check dependencies
pip list | grep streamlit
pip list | grep openai

# Verify Git status
git status
git log --oneline -5

# Push to GitHub
git add .
git commit -m "Ready for deployment"
git push origin main
```

## Deployment Links

- **Streamlit Cloud**: [share.streamlit.io](https://share.streamlit.io)
- **OpenAI Dashboard**: [platform.openai.com/usage](https://platform.openai.com/usage)
- **Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)

---

## Troubleshooting

**App won't start?**
- Check logs in Streamlit Cloud dashboard
- Verify all secrets are set correctly
- Ensure `requirements.txt` includes all dependencies

**PDF upload not working?**
- Check `packages.txt` includes `poppler-utils`
- Verify file size is under 20MB
- Test PDF compression tool link

**API key errors?**
- Verify secrets are saved in Streamlit Cloud
- Check key format (OpenAI keys start with `sk-`)
- Test keys in OpenAI playground first

---

✅ **Ready to deploy?** Follow [DEPLOYMENT.md](DEPLOYMENT.md) for step-by-step instructions!
