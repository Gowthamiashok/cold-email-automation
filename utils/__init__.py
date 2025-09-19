"""
Cold Email Automation Utils Package
Core utility modules for Gmail authentication, email sending, and AI integration
"""

__version__ = "1.0.0"
__author__ = "Cold Email Automation Team"

# Import core modules
from .gmail_auth import GmailAuthenticator
from .email_sender import EmailSender
from .gemini_ai import GeminiAI

__all__ = [
    'GmailAuthenticator',
    'EmailSender', 
    'GeminiAI'
]
