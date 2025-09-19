# 🚀 Deployment Checklist

## Pre-Deployment
- [ ] All environment variables configured
- [ ] Google Cloud Console OAuth settings updated
- [ ] App published (not in testing mode)
- [ ] All code committed to GitHub
- [ ] Repository is public (or you have paid Streamlit plan)

## Deployment Steps
- [ ] Go to https://share.streamlit.io
- [ ] Sign in with GitHub
- [ ] Click "New app"
- [ ] Select your repository
- [ ] Set main file: app.py
- [ ] Add environment variables in secrets
- [ ] Click "Deploy"

## Post-Deployment
- [ ] Test the deployed app
- [ ] Update Google Cloud Console with new redirect URI
- [ ] Share the app URL with friends
- [ ] Monitor usage and performance

## Your App URL
https://[your-app-name].streamlit.app

## Environment Variables to Set
- GOOGLE_CLIENT_ID
- GOOGLE_CLIENT_SECRET
- GEMINI_API_KEY

## Live Updates
- Make changes locally
- Test thoroughly
- `git add . && git commit -m "Update" && git push`
- Wait 1-2 minutes for automatic deployment
