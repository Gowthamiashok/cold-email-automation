"""
Gmail OAuth2 Authentication Module
Handles Google OAuth2 flow for Gmail API access
"""

import os
import streamlit as st
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import json
import urllib.parse

class GmailAuthenticator:
    """Handles Gmail OAuth2 authentication and service creation"""
    
    # Required scopes for Gmail API access
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.send',           # Send emails
        'https://www.googleapis.com/auth/gmail.readonly',       # Read user profile
        'https://www.googleapis.com/auth/drive.readonly'        # Access files from Drive (optional)
    ]
    
    def __init__(self):
        """Initialize the Gmail authenticator"""
        self.credentials = None
        self.service = None
        
    def get_credentials_from_env(self):
        """Get OAuth2 credentials from environment variables"""
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            raise ValueError("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in environment")
        
        # Detect if running locally or deployed
        if os.getenv('STREAMLIT_SERVER_PORT'):
            # Running on Streamlit Cloud
            redirect_uri = "https://cold-email-automation-webapp.streamlit.app"
        else:
            # Running locally
            redirect_uri = "http://localhost:8501"
        
        return {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri]
            }
        }
    
    def authenticate(self):
        """Perform OAuth2 authentication flow"""
        try:
            # Check if credentials are already in session state
            if 'gmail_credentials' in st.session_state:
                try:
                    # Handle both string and dict formats
                    creds_data = st.session_state.gmail_credentials
                    if isinstance(creds_data, str):
                        creds_data = json.loads(creds_data)
                    
                    self.credentials = Credentials.from_authorized_user_info(
                        creds_data, self.SCOPES
                    )
                except (json.JSONDecodeError, TypeError) as e:
                    st.warning(f"Invalid credentials format: {e}")
                    # Clear invalid credentials
                    del st.session_state.gmail_credentials
                    self.credentials = None
            
            # If credentials are not valid, start OAuth flow
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    try:
                        self.credentials.refresh(Request())
                    except Exception as e:
                        st.warning(f"Token refresh failed: {e}")
                        self.credentials = None
                
                if not self.credentials:
                    # Create OAuth flow with proper redirect URI
                    client_config = self.get_credentials_from_env()
                    
                    # Ensure redirect URI is properly set
                    # Detect if running locally or deployed
                    if os.getenv('STREAMLIT_SERVER_PORT'):
                        # Running on Streamlit Cloud
                        redirect_uri = "https://cold-email-automation-webapp.streamlit.app"
                    else:
                        # Running locally
                        redirect_uri = "http://localhost:8501"
                    client_config["installed"]["redirect_uris"] = [redirect_uri]
                    
                    flow = InstalledAppFlow.from_client_config(
                        client_config, self.SCOPES, redirect_uri=redirect_uri
                    )
                    
                    # Get authorization URL
                    auth_url, _ = flow.authorization_url(
                        prompt='consent',
                        access_type='offline',
                        include_granted_scopes='true'
                    )
                    
                    st.markdown(f"""
                    ### 🔐 Gmail Authentication Required
                    
                    Please click the link below to authorize access to your Gmail account:
                    
                    **[Authorize Gmail Access]({auth_url})**
                    
                    After authorization, you'll be redirected back to this application.
                    
                    **Note:** Make sure your Google Cloud Console project has the correct redirect URI 
                    added to the authorized redirect URIs.
                    """)
                    
                    return False
                
                # Store credentials in session state
                st.session_state.gmail_credentials = self.credentials.to_json()
            
            return True
            
        except Exception as e:
            st.error(f"Authentication error: {str(e)}")
            # Clear any invalid session state
            if 'gmail_credentials' in st.session_state:
                del st.session_state.gmail_credentials
            return False
    
    def get_service(self):
        """Get authenticated Gmail service"""
        if not self.credentials:
            if not self.authenticate():
                return None
        
        try:
            if not self.service:
                self.service = build('gmail', 'v1', credentials=self.credentials)
            return self.service
        except Exception as e:
            st.error(f"Failed to create Gmail service: {str(e)}")
            return None
    
    def is_authenticated(self):
        """Check if user is authenticated"""
        try:
            if 'gmail_credentials' not in st.session_state:
                return False
            
            # Parse credentials from session state
            creds_data = st.session_state.gmail_credentials
            if isinstance(creds_data, str):
                creds_data = json.loads(creds_data)
            
            # Create credentials object
            self.credentials = Credentials.from_authorized_user_info(
                creds_data, self.SCOPES
            )
            
            # Check if credentials are valid
            if not self.credentials.valid:
                if self.credentials.expired and self.credentials.refresh_token:
                    try:
                        self.credentials.refresh(Request())
                        # Update session state with refreshed credentials
                        st.session_state.gmail_credentials = self.credentials.to_json()
                    except Exception as e:
                        st.warning(f"Token refresh failed: {e}")
                        return False
            
            return self.credentials is not None and self.credentials.valid
            
        except Exception as e:
            st.warning(f"Authentication check failed: {e}")
            return False
    
    def get_user_info(self):
        """Get authenticated user's Gmail profile information"""
        service = self.get_service()
        if not service:
            return None
        
        try:
            profile = service.users().getProfile(userId='me').execute()
            return profile
        except Exception as e:
            st.error(f"Failed to get user info: {str(e)}")
            return None
    
    def handle_oauth_callback(self):
        """Handle OAuth callback from URL parameters"""
        try:
            # Check if we have authorization code in URL
            query_params = st.query_params
            
            if 'code' in query_params:
                # We have an authorization code, complete the flow
                client_config = self.get_credentials_from_env()
                # Detect if running locally or deployed
                if os.getenv('STREAMLIT_SERVER_PORT'):
                    # Running on Streamlit Cloud
                    redirect_uri = "https://cold-email-automation-webapp.streamlit.app"
                else:
                    # Running locally
                    redirect_uri = "http://localhost:8501"
                
                flow = InstalledAppFlow.from_client_config(
                    client_config, self.SCOPES, redirect_uri=redirect_uri
                )
                
                # Exchange authorization code for credentials
                flow.fetch_token(code=query_params['code'])
                
                # Store credentials properly
                self.credentials = flow.credentials
                st.session_state.gmail_credentials = self.credentials.to_json()
                
                # Clear URL parameters
                st.query_params.clear()
                
                st.success("✅ Gmail authentication successful!")
                st.rerun()
                return True
                
        except Exception as e:
            st.error(f"OAuth callback error: {str(e)}")
            # Clear any invalid session state
            if 'gmail_credentials' in st.session_state:
                del st.session_state.gmail_credentials
            
        return False
    
    def debug_credentials(self):
        """Debug function to check credentials status"""
        try:
            if 'gmail_credentials' in st.session_state:
                creds_data = st.session_state.gmail_credentials
                st.write(f"**Credentials type:** {type(creds_data)}")
                if isinstance(creds_data, str):
                    st.write(f"**Credentials length:** {len(creds_data)}")
                    try:
                        parsed = json.loads(creds_data)
                        st.write(f"**Parsed keys:** {list(parsed.keys())}")
                        
                        # Check if credentials object is valid
                        if self.credentials:
                            st.write(f"**Credentials valid:** {self.credentials.valid}")
                            st.write(f"**Credentials expired:** {self.credentials.expired}")
                            st.write(f"**Has refresh token:** {bool(self.credentials.refresh_token)}")
                        else:
                            st.write("**Credentials object:** Not created")
                            
                    except Exception as e:
                        st.write(f"**Parse error:** {e}")
                else:
                    st.write(f"**Credentials keys:** {list(creds_data.keys())}")
            else:
                st.write("**No credentials in session state**")
                
            # Test authentication status
            auth_status = self.is_authenticated()
            st.write(f"**Authentication status:** {auth_status}")
            
        except Exception as e:
            st.write(f"**Debug error:** {e}")
    
    def logout(self):
        """Clear authentication credentials"""
        if 'gmail_credentials' in st.session_state:
            del st.session_state.gmail_credentials
        self.credentials = None
        self.service = None
