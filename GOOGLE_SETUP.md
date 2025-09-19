# Google Cloud Console Setup Guide

## Fixing Gmail OAuth2 Authentication Issues

### Step 1: Google Cloud Console Configuration

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create or Select Project**
   - Click "Select a project" → "New Project"
   - Name: "Cold Email Automation" (or any name you prefer)
   - Click "Create"

3. **Enable Gmail API**
   - Go to "APIs & Services" → "Library"
   - Search for "Gmail API"
   - Click on "Gmail API" → "Enable"

4. **Create OAuth2 Credentials**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Application type: "Desktop application"
   - Name: "Cold Email App"

5. **Configure OAuth Consent Screen**
   - Go to "APIs & Services" → "OAuth consent screen"
   - User Type: "External" (unless you have Google Workspace)
   - Fill in required fields:
     - App name: "Cold Email Automation"
     - User support email: Your email
     - Developer contact: Your email
   - Click "Save and Continue"
   - Scopes: Add these scopes:
     - `https://www.googleapis.com/auth/gmail.send`
     - `https://www.googleapis.com/auth/gmail.readonly`
     - `https://www.googleapis.com/auth/drive.readonly`
   - Test users: Add your Gmail address
   - Click "Save and Continue"

6. **Set Redirect URIs**
   - Go back to "Credentials"
   - Click on your OAuth client ID
   - Under "Authorized redirect URIs", add:
     - `http://localhost:8501`
   - Click "Save"

### Step 2: Get Your Credentials

1. **Download Credentials**
   - In your OAuth client ID page
   - Click "Download JSON"
   - Save the file as `credentials.json` in your project folder

2. **Extract Client ID and Secret**
   - Open the downloaded JSON file
   - Copy the `client_id` value
   - Copy the `client_secret` value
   - Add these to your `.env` file:

```env
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### Step 3: Test the Authentication

1. **Restart Streamlit**
   ```bash
   streamlit run app.py
   ```

2. **Test Gmail Connection**
   - Go to "Authentication" tab
   - Click "Connect Gmail Account"
   - Click the authorization link
   - Complete the OAuth flow
   - You should see "✅ Gmail authentication successful!"

### Common Issues & Solutions

#### Issue: "Access blocked: Authorization Error"
**Solution:** Make sure `http://localhost:8501` is added to authorized redirect URIs

#### Issue: "Missing required parameter: redirect_uri"
**Solution:** Check that your OAuth client ID has the correct redirect URI configured

#### Issue: "This app isn't verified"
**Solution:** This is normal for development. Click "Advanced" → "Go to Cold Email Automation (unsafe)"

#### Issue: "Error 400: invalid_request"
**Solution:** 
- Verify your client ID and secret are correct
- Ensure redirect URI matches exactly: `http://localhost:8501`
- Check that Gmail API is enabled

### Step 4: Gemini API Setup

1. **Get Gemini API Key**
   - Go to: https://makersuite.google.com/app/apikey
   - Click "Create API Key"
   - Copy the key to your `.env` file

2. **Test Gemini Connection**
   - The app will automatically test Gemini when you preview emails

### Verification Checklist

- [ ] Google Cloud project created
- [ ] Gmail API enabled
- [ ] OAuth consent screen configured
- [ ] OAuth client ID created (Desktop application)
- [ ] Redirect URI added: `http://localhost:8501`
- [ ] Client ID and Secret added to `.env`
- [ ] Gemini API key added to `.env`
- [ ] Streamlit app restarted
- [ ] Gmail authentication successful

### Troubleshooting Commands

```bash
# Check environment variables
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('GOOGLE_CLIENT_ID:', bool(os.getenv('GOOGLE_CLIENT_ID'))); print('GOOGLE_CLIENT_SECRET:', bool(os.getenv('GOOGLE_CLIENT_SECRET'))); print('GEMINI_API_KEY:', bool(os.getenv('GEMINI_API_KEY')))"

# Test Gmail authentication
python -c "from utils.gmail_auth import GmailAuthenticator; auth = GmailAuthenticator(); print('Auth test:', auth.authenticate())"
```

If you're still having issues, please share:
1. Your Google Cloud Console project settings
2. The exact error message
3. Your `.env` file structure (without the actual keys)
