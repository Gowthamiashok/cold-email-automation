"""
Test Setup Script for Cold Email Automation App
Validates environment, dependencies, and basic functionality
"""

import sys
import os
import importlib

def test_python_version():
    """Test Python version compatibility"""
    print("🐍 Testing Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def test_dependencies():
    """Test if all required dependencies are installed"""
    print("\n📦 Testing dependencies...")
    required_packages = [
        'streamlit',
        'google-api-python-client',
        'google-auth',
        'google-auth-oauthlib',
        'google-generativeai',
        'pandas',
        'openpyxl',
        'python-dotenv',
        'requests',
        'PyPDF2'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            importlib.import_module(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All dependencies installed")
        return True

def test_environment_variables():
    """Test environment variable configuration"""
    print("\n🔧 Testing environment variables...")
    
    # Load .env file if it exists
    if os.path.exists('.env'):
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ .env file found and loaded")
    else:
        print("⚠️  .env file not found - using system environment")
    
    required_vars = ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'GEMINI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            masked_value = value[:8] + "..." if len(value) > 8 else "***"
            print(f"✅ {var}: {masked_value}")
        else:
            print(f"❌ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Copy env.example to .env and fill in your values")
        return False
    else:
        print("\n✅ All environment variables configured")
        return True

def test_imports():
    """Test if our custom modules can be imported"""
    print("\n📁 Testing custom module imports...")
    
    try:
        from utils.gmail_auth import GmailAuthenticator
        print("✅ GmailAuthenticator imported")
    except Exception as e:
        print(f"❌ GmailAuthenticator import failed: {e}")
        return False
    
    try:
        from utils.gemini_ai import GeminiAI
        print("✅ GeminiAI imported")
    except Exception as e:
        print(f"❌ GeminiAI import failed: {e}")
        return False
    
    try:
        from utils.email_sender import EmailSender
        print("✅ EmailSender imported")
    except Exception as e:
        print(f"❌ EmailSender import failed: {e}")
        return False
    
    print("✅ All custom modules imported successfully")
    return True

def test_gemini_connection():
    """Test Gemini AI connection"""
    print("\n🤖 Testing Gemini AI connection...")
    
    try:
        from utils.gemini_ai import GeminiAI
        gemini = GeminiAI()
        
        if gemini.test_connection():
            print("✅ Gemini AI connection successful")
            return True
        else:
            print("❌ Gemini AI connection failed")
            return False
    except Exception as e:
        print(f"❌ Gemini AI test error: {e}")
        return False

def test_virtual_environment():
    """Test if running in virtual environment"""
    print("🔒 Testing virtual environment...")
    
    # Check if we're in a virtual environment
    in_venv = (
        hasattr(sys, 'real_prefix') or 
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) or
        os.environ.get('VIRTUAL_ENV') is not None
    )
    
    if in_venv:
        venv_path = os.environ.get('VIRTUAL_ENV', 'Unknown')
        print(f"✅ Running in virtual environment: {venv_path}")
        return True
    else:
        print("⚠️  Not running in virtual environment")
        print("   Recommended: python -m venv venv && source venv/bin/activate (Linux/Mac)")
        print("   Recommended: python -m venv venv && venv\\Scripts\\activate (Windows)")
        return False

def main():
    """Run all tests"""
    print("🧪 Cold Email Automation App - Setup Test")
    print("=" * 50)
    
    tests = [
        test_python_version,
        test_virtual_environment,
        test_dependencies,
        test_environment_variables,
        test_imports,
        test_gemini_connection
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready to run the app.")
        print("\nNext steps:")
        print("1. Run: streamlit run app.py")
        print("2. Open browser to http://localhost:8501")
        print("3. Test Gmail authentication")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
    
    return passed == total

if __name__ == "__main__":
    main()
