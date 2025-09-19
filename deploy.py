#!/usr/bin/env python3
"""
Deployment Helper Script for Cold Email Automation App
This script helps prepare your app for deployment on Streamlit Community Cloud
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if all required files exist"""
    required_files = [
        'app.py',
        'requirements.txt',
        '.env.example',
        'README.md'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files present")
    return True

def check_environment():
    """Check if environment variables are set"""
    required_vars = [
        'GOOGLE_CLIENT_ID',
        'GOOGLE_CLIENT_SECRET',
        'GEMINI_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Set these in your .env file or Streamlit secrets")
        return False
    
    print("✅ Environment variables configured")
    return True

def create_gitignore():
    """Create or update .gitignore file"""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# Environment Variables
.env
.streamlit/secrets.toml

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Temporary files
*.tmp
*.temp
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    
    print("✅ .gitignore file created/updated")

def check_git_status():
    """Check git repository status"""
    try:
        # Check if git is initialized
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Git repository not initialized")
            return False
        
        # Check for uncommitted changes
        if "nothing to commit" not in result.stdout:
            print("⚠️  You have uncommitted changes")
            print("💡 Run: git add . && git commit -m 'Prepare for deployment'")
            return False
        
        print("✅ Git repository ready")
        return True
        
    except FileNotFoundError:
        print("❌ Git not installed")
        return False

def create_deployment_checklist():
    """Create deployment checklist"""
    checklist = """
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
"""
    
    with open('DEPLOYMENT_CHECKLIST.md', 'w') as f:
        f.write(checklist)
    
    print("✅ Deployment checklist created")

def main():
    """Main deployment helper function"""
    print("🚀 Cold Email Automation App - Deployment Helper")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Please ensure all required files exist before deploying")
        return False
    
    # Create/update .gitignore
    create_gitignore()
    
    # Check environment
    check_environment()
    
    # Check git status
    check_git_status()
    
    # Create deployment checklist
    create_deployment_checklist()
    
    print("\n🎉 Deployment preparation complete!")
    print("\n📋 Next steps:")
    print("1. Review DEPLOYMENT_CHECKLIST.md")
    print("2. Follow the deployment guide")
    print("3. Deploy on Streamlit Community Cloud")
    print("4. Update Google Cloud Console settings")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
