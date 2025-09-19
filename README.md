# Cold Email Automation Web App

A Streamlit web application that converts your existing N8N cold email workflow into a user-friendly tool for automated personalized email campaigns.

## Features

- 🔐 **Gmail OAuth2 Integration**: Users connect their own Gmail accounts
- 📊 **File Upload**: Support for CSV/Excel company data and PDF resumes
- 🤖 **AI Personalization**: Free Gemini API integration for email customization
- 📧 **Email Automation**: Send emails from users' own Gmail accounts
- 📈 **Campaign Tracking**: Real-time progress monitoring and results export
- ⚡ **Rate Limiting**: Built-in delays to respect API quotas

## Quick Start

### 🚀 Deploy Online (Recommended for Friends)

**Deploy your app for free on Streamlit Community Cloud:**

1. **Prepare for deployment:**
   ```bash
   python deploy.py  # Run deployment helper
   ```

2. **Follow the deployment guide:**
   - Read `DEPLOYMENT_GUIDE.md` for detailed instructions
   - Deploy on [share.streamlit.io](https://share.streamlit.io)
   - Share the URL with your friends!

3. **Live updates:**
   - Make changes locally
   - Push to GitHub
   - App updates automatically in 1-2 minutes!

### 💻 Local Development Setup

#### 1. Automated Setup (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd cold_email_app

# Run automated setup script
python setup.py
```

The setup script will:
- Create a virtual environment
- Install all dependencies
- Create .env file from template
- Run validation tests

### 2. Manual Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd cold_email_app

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Setup

```bash
# Copy environment template (if not done by setup script)
cp env.example .env

# Edit .env with your credentials
# - GOOGLE_CLIENT_ID: From Google Cloud Console
# - GOOGLE_CLIENT_SECRET: From Google Cloud Console  
# - GEMINI_API_KEY: From Google AI Studio
```

### 4. Google API Setup

#### Gmail API Setup:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth2 credentials
5. Add `http://localhost:8501` to authorized redirect URIs

#### Gemini API Setup:
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file

### 5. Run the Application

```bash
# Make sure virtual environment is activated
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Run the application
streamlit run app.py
```

## Project Structure

```
cold_email_app/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Dependencies list
├── env.example           # Template for environment variables
├── .gitignore           # Git ignore file
├── README.md            # Project documentation
└── utils/
    ├── __init__.py
    ├── gmail_auth.py    # Gmail OAuth handling
    ├── email_sender.py  # Email automation logic
    └── gemini_ai.py     # AI content generation
```

## Usage

1. **Authentication**: Connect your Gmail account via OAuth2
2. **Data Upload**: Upload company data (CSV/Excel) and resume (PDF)
3. **Template Setup**: Customize your email template
4. **Campaign Launch**: Start your email campaign with progress tracking
5. **Results Export**: Download campaign results and statistics

## API Limits & Rate Limiting

### Gemini API (Free Tier)
- **Model**: `gemini-1.5-flash` (FREE)
- **Daily Limit**: 1,500 requests
- **Rate Limit**: 15 requests per minute
- **App Delay**: 4+ seconds between calls

### Gmail API
- **Daily Quota**: 1 billion quota units
- **Send Limit**: 100 emails per second (conservative: 1 per minute)
- **App Delay**: 60 seconds between emails

## Development

### Testing Components
- Gmail authentication flow
- Gemini AI integration
- Email sending functionality
- File upload and processing

### Deployment

#### Free Deployment Options
- **Streamlit Community Cloud**: Recommended for free hosting
- **Railway**: Alternative with private repo support
- **Heroku**: Paid option with more features

#### Deployment Features
- **Live Updates**: Automatic deployment from GitHub
- **Environment Variables**: Secure secrets management
- **HTTPS**: Secure connections for OAuth
- **Monitoring**: Built-in usage statistics

#### Quick Deployment Steps
1. Push code to GitHub repository
2. Connect to Streamlit Community Cloud
3. Add environment variables
4. Deploy and share URL with friends!

See `DEPLOYMENT_GUIDE.md` for detailed instructions.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Check the troubleshooting section
- Review API documentation
- Open an issue on GitHub
