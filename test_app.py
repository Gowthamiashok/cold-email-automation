"""
Streamlit App Test Script
Tests the main application functionality
"""

import streamlit as st
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_app_import():
    """Test if the main app can be imported"""
    try:
        import app
        print("✅ Main app imported successfully")
        return True
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False

def test_utils_import():
    """Test if utils can be imported"""
    try:
        from utils import GmailAuthenticator, EmailSender, GeminiAI
        print("✅ Utils imported successfully")
        return True
    except Exception as e:
        print(f"❌ Utils import failed: {e}")
        return False

def test_gemini_basic():
    """Test basic Gemini functionality"""
    try:
        from utils.gemini_ai import GeminiAI
        gemini = GeminiAI()
        
        # Test usage info
        info = gemini.get_usage_info()
        print(f"✅ Gemini info: {info['status']}")
        
        # Test basic generation
        test_content = gemini.personalize_email(
            "Test Company", 
            "John Doe", 
            "Hello [Recruiter Name], I'm interested in opportunities at [Company Name]."
        )
        
        if test_content and len(test_content) > 10:
            print("✅ Gemini content generation working")
            return True
        else:
            print("❌ Gemini content generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Gemini test failed: {e}")
        return False

def test_email_validation():
    """Test email validation logic"""
    try:
        import pandas as pd
        from utils.email_sender import EmailSender
        
        sender = EmailSender()
        
        # Test valid data
        valid_data = pd.DataFrame({
            'Company Name': ['Test Company'],
            'Recruiter': ['John Doe'],
            'Email': ['test@example.com']
        })
        
        is_valid, errors = sender.validate_company_data(valid_data)
        if is_valid:
            print("✅ Email validation working")
            return True
        else:
            print(f"❌ Email validation failed: {errors}")
            return False
            
    except Exception as e:
        print(f"❌ Email validation test failed: {e}")
        return False

def main():
    """Run app tests"""
    print("🧪 Cold Email App - Application Tests")
    print("=" * 50)
    
    tests = [
        test_app_import,
        test_utils_import,
        test_gemini_basic,
        test_email_validation
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
    print(f"📊 App Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 App tests passed! Ready to run Streamlit.")
    else:
        print("⚠️  Some app tests failed.")
    
    return passed == total

if __name__ == "__main__":
    main()
