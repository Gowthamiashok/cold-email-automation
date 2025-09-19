"""
Email Sending Module
Handles email composition, sending, and campaign management
"""

import os
import time
import base64
import streamlit as st
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import List, Dict, Optional, Tuple
from .gmail_auth import GmailAuthenticator
from .gemini_ai import GeminiAI

class EmailSender:
    """Handles email composition, sending, and campaign tracking"""
    
    # Rate limiting configuration
    GMAIL_DELAY_SECONDS = 60  # Default 1-minute delay between emails
    MAX_ATTACHMENT_SIZE = 25 * 1024 * 1024  # 25MB Gmail limit
    
    def __init__(self):
        """Initialize email sender with authentication and AI"""
        self.gmail_auth = GmailAuthenticator()
        self.gemini_ai = GeminiAI()
        self.campaign_results = []
    
    def validate_company_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate uploaded company data
        
        Args:
            df: DataFrame containing company data
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        required_columns = ['Company Name', 'Recruiter', 'Email']
        
        # Check required columns
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            errors.append(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Check for empty values
        for col in required_columns:
            if col in df.columns and df[col].isna().any():
                errors.append(f"Column '{col}' contains empty values")
        
        # Check email format (basic validation)
        if 'Email' in df.columns:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            invalid_emails = df[~df['Email'].str.match(email_pattern, na=False)]
            if not invalid_emails.empty:
                errors.append(f"Invalid email addresses found: {len(invalid_emails)} rows")
        
        return len(errors) == 0, errors
    
    def create_email_message(self, to_email: str, subject: str, body: str, 
                           attachment_path: Optional[str] = None, attachment_name: Optional[str] = None) -> str:
        """
        Create email message with optional attachment
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            body: Email body content
            attachment_path: Optional path to PDF attachment
            
        Returns:
            Base64 encoded email message
        """
        message = MIMEMultipart()
        message['to'] = to_email
        message['subject'] = subject
        
        # Convert plain text to HTML with proper formatting
        html_body = self._convert_text_to_html(body)
        
        # Add email body as HTML
        message.attach(MIMEText(html_body, 'html'))
        
        # Add attachment if provided
        if attachment_path and os.path.exists(attachment_path):
            try:
                with open(attachment_path, 'rb') as attachment:
                    # Use provided attachment name or fallback to basename
                    filename = attachment_name if attachment_name else os.path.basename(attachment_path)
                    part = MIMEApplication(
                        attachment.read(),
                        Name=filename
                    )
                    part['Content-Disposition'] = f'attachment; filename="{filename}"'
                    message.attach(part)
            except Exception as e:
                st.warning(f"Failed to attach file: {str(e)}")
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return raw_message
    
    def _convert_text_to_html(self, text: str) -> str:
        """
        Convert plain text to HTML with proper formatting
        
        Args:
            text: Plain text content
            
        Returns:
            HTML formatted content
        """
        # Split text into paragraphs and format properly
        paragraphs = text.split('\n\n')
        
        # Create HTML paragraphs with minimal spacing
        html_paragraphs = []
        for paragraph in paragraphs:
            if paragraph.strip():  # Skip empty paragraphs
                # Replace single line breaks within paragraphs with <br>
                formatted_paragraph = paragraph.strip().replace('\n', '<br>')
                html_paragraphs.append(f'<p style="margin: 8px 0; line-height: 1.4;">{formatted_paragraph}</p>')
        
        # Join paragraphs
        html_text = '\n'.join(html_paragraphs)
        
        # Wrap in proper HTML structure
        html_content = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.4;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
            </style>
        </head>
        <body>
            {html_text}
        </body>
        </html>
        """
        
        return html_content
    
    def send_email(self, to_email: str, subject: str, body: str, 
                   attachment_path: Optional[str] = None, attachment_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Send a single email
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            body: Email body content
            attachment_path: Optional path to PDF attachment
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Get Gmail service
            service = self.gmail_auth.get_service()
            if not service:
                return False, "Gmail service not available"
            
            # Create email message
            raw_message = self.create_email_message(to_email, subject, body, attachment_path, attachment_name)
            
            # Send email
            message = service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return True, f"Email sent successfully (ID: {message['id']})"
            
        except Exception as e:
            return False, f"Failed to send email: {str(e)}"
    
    def run_campaign(self, company_data: pd.DataFrame, email_template: str, 
                    subject_template: str, resume_path: Optional[str] = None,
                    resume_name: Optional[str] = None, delay_seconds: int = 60, progress_callback=None) -> List[Dict]:
        """
        Run email campaign for all companies in the data
        
        Args:
            company_data: DataFrame with company information
            email_template: Base email template
            subject_template: Email subject template
            resume_path: Optional path to resume PDF
            progress_callback: Optional callback function for progress updates
            
        Returns:
            List of campaign results
        """
        self.campaign_results = []
        total_emails = len(company_data)
        
        st.info(f"Starting campaign for {total_emails} companies...")
        
        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for index, row in company_data.iterrows():
            try:
                # Update progress
                progress = (index + 1) / total_emails
                progress_bar.progress(progress)
                
                company_name = row['Company Name']
                recruiter_name = row['Recruiter']
                email_address = row['Email']
                
                status_text.text(f"Sending to {company_name} ({index + 1}/{total_emails})")
                
                # Check personalization mode
                personalization_mode = st.session_state.get('personalization_mode', '🤖 AI-Powered Personalization')
                
                if personalization_mode == "🤖 AI-Powered Personalization":
                    # Check if user has edited preview content
                    if 'preview_email_content' in st.session_state:
                        # Use the edited content as base template
                        personalized_body = st.session_state['preview_email_content']
                        # Replace placeholders for this specific company
                        personalized_body = personalized_body.replace("[Company Name]", company_name)
                        personalized_body = personalized_body.replace("[Recruiter Name]", recruiter_name)
                        personalized_body = personalized_body.replace("[COMPANY]", company_name)
                        personalized_body = personalized_body.replace("[RECRUITER]", recruiter_name)
                    else:
                        # Extract resume content if available
                        resume_summary = ""
                        if 'resume_file' in st.session_state:
                            resume_summary = self.gemini_ai.extract_resume_content(st.session_state['resume_file'])
                        
                        # Get company data for this row
                        company_data = row.to_dict()
                        
                        # Generate personalized content
                        personalized_body = self.gemini_ai.personalize_email(
                            company_name, recruiter_name, email_template, resume_summary, company_data
                        )
                else:
                    # Manual template mode - simple replacement
                    personalized_body = email_template.replace("[Company Name]", company_name)
                    personalized_body = personalized_body.replace("[Recruiter Name]", recruiter_name)
                    personalized_body = personalized_body.replace("[COMPANY]", company_name)
                    personalized_body = personalized_body.replace("[RECRUITER]", recruiter_name)
                
                # Personalize subject
                if 'preview_email_subject' in st.session_state:
                    # Use edited subject as base
                    personalized_subject = st.session_state['preview_email_subject']
                    # Replace placeholders for this specific company
                    personalized_subject = personalized_subject.replace("[Company Name]", company_name)
                    personalized_subject = personalized_subject.replace("[Recruiter Name]", recruiter_name)
                else:
                    # Use original subject template
                    personalized_subject = subject_template.replace("[Company Name]", company_name)
                    personalized_subject = personalized_subject.replace("[Recruiter Name]", recruiter_name)
                
                # Send email
                success, message = self.send_email(
                    email_address, personalized_subject, personalized_body, resume_path, resume_name
                )
                
                # Record result
                result = {
                    'company': company_name,
                    'recruiter': recruiter_name,
                    'email': email_address,
                    'subject': personalized_subject,
                    'success': success,
                    'message': message,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                self.campaign_results.append(result)
                
                # Call progress callback if provided
                if progress_callback:
                    progress_callback(result)
                
                # Rate limiting delay
                if index < total_emails - 1:  # Don't delay after last email
                    time.sleep(delay_seconds)
                
            except Exception as e:
                # Record error
                error_result = {
                    'company': row.get('Company Name', 'Unknown'),
                    'recruiter': row.get('Recruiter', 'Unknown'),
                    'email': row.get('Email', 'Unknown'),
                    'subject': 'Error',
                    'success': False,
                    'message': f"Campaign error: {str(e)}",
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                self.campaign_results.append(error_result)
        
        # Final progress update
        progress_bar.progress(1.0)
        status_text.text("Campaign completed!")
        
        return self.campaign_results
    
    def get_campaign_summary(self) -> Dict[str, int]:
        """Get summary statistics of the campaign"""
        if not self.campaign_results:
            return {'total': 0, 'successful': 0, 'failed': 0}
        
        total = len(self.campaign_results)
        successful = sum(1 for result in self.campaign_results if result['success'])
        failed = total - successful
        
        return {
            'total': total,
            'successful': successful,
            'failed': failed
        }
    
    def export_results(self, filename: str = None) -> str:
        """Export campaign results to CSV"""
        if not self.campaign_results:
            return None
        
        if not filename:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f"campaign_results_{timestamp}.csv"
        
        # Create DataFrame and export
        df_results = pd.DataFrame(self.campaign_results)
        df_results.to_csv(filename, index=False)
        
        return filename
