"""
Cold Email Automation Web App
Main Streamlit application for multi-user email automation
"""

import streamlit as st
import os
import pandas as pd
import time
from dotenv import load_dotenv
from utils.gmail_auth import GmailAuthenticator
from utils.gemini_ai import GeminiAI
from utils.email_sender import EmailSender

# Load environment variables
load_dotenv()

def check_environment():
    """Check if all required environment variables are configured"""
    required_vars = ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'GEMINI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    return len(missing_vars) == 0, missing_vars

def gmail_auth_section():
    """Gmail authentication section"""
    st.subheader("🔐 Gmail Authentication")
    
    gmail_auth = GmailAuthenticator()
    
    # Handle OAuth callback first
    gmail_auth.handle_oauth_callback()
    
    # Debug section (collapsible)
    with st.expander("🔧 Debug Information"):
        gmail_auth.debug_credentials()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear Session State"):
                if 'gmail_credentials' in st.session_state:
                    del st.session_state.gmail_credentials
                st.rerun()
        
        with col2:
            if st.button("Test Gmail Connection"):
                try:
                    service = gmail_auth.get_service()
                    if service:
                        profile = service.users().getProfile(userId='me').execute()
                        st.success(f"✅ Gmail connection successful! Email: {profile.get('emailAddress')}")
                    else:
                        st.error("❌ Gmail service not available")
                except Exception as e:
                    st.error(f"❌ Gmail connection test failed: {str(e)}")
    
    if gmail_auth.is_authenticated():
        # Get user info
        user_info = gmail_auth.get_user_info()
        if user_info:
            st.success(f"✅ Connected as: {user_info.get('emailAddress', 'Unknown')}")
            st.info(f"📊 Total messages: {user_info.get('messagesTotal', 'Unknown')}")
            
            if st.button("🔌 Disconnect Gmail"):
                gmail_auth.logout()
                st.rerun()
        else:
            st.warning("⚠️ Connected but unable to fetch user info")
    else:
        st.info("🔗 Connect your Gmail account to start sending emails")
        
        if st.button("🔐 Connect Gmail Account"):
            try:
                if gmail_auth.authenticate():
                    st.success("✅ Gmail authentication successful!")
                    st.rerun()
                else:
                    st.error("❌ Gmail authentication failed")
            except Exception as e:
                st.error(f"❌ Authentication error: {str(e)}")
                st.info("💡 Try clearing session state and reconnecting")

def file_upload_section():
    """File upload section for company data and resume"""
    st.subheader("📁 Upload Files")
    
    # Company data upload
    st.write("**Company Data (CSV/Excel)**")
    st.info("Required columns: Company Name, Recruiter, Email")
    
    company_file = st.file_uploader(
        "Choose company data file",
        type=['csv', 'xlsx', 'xls'],
        key="company_file"
    )
    
    if company_file:
        try:
            if company_file.name.endswith('.csv'):
                df = pd.read_csv(company_file)
            else:
                df = pd.read_excel(company_file)
            
            st.success(f"✅ File uploaded: {company_file.name}")
            st.write(f"📊 Rows: {len(df)}, Columns: {len(df.columns)}")
            
            # Show preview
            st.write("**Preview:**")
            st.dataframe(df.head())
            
            # Validate data
            email_sender = EmailSender()
            is_valid, errors = email_sender.validate_company_data(df)
            
            if is_valid:
                st.success("✅ Data validation passed")
                st.session_state['company_data'] = df
            else:
                st.error("❌ Data validation failed:")
                for error in errors:
                    st.error(f"• {error}")
                    
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
    
    # Resume upload
    st.write("**Resume (PDF)**")
    resume_file = st.file_uploader(
        "Choose resume file",
        type=['pdf'],
        key="resume_file"
    )
    
    if resume_file:
        st.success(f"✅ Resume uploaded: {resume_file.name}")
        # Note: resume_file is automatically stored in st.session_state.resume_file
        # No need to manually assign it

def email_template_section():
    """Email template customization section"""
    st.subheader("✉️ Email Template")
    
    # Personalization mode selection
    personalization_mode = st.radio(
        "Choose Email Personalization Mode:",
        ["🤖 AI-Powered Personalization", "✏️ Manual Template"],
        help="AI mode generates personalized content based on resume and company research. Manual mode uses your template."
    )
    
    # Clear preview when switching modes
    if 'personalization_mode' in st.session_state and st.session_state['personalization_mode'] != personalization_mode:
        # Clear all preview-related session state when switching modes
        preview_keys = ['preview_content', 'preview_subject', 'preview_company', 'preview_recruiter', 
                       'preview_email', 'preview_resume_summary', 'preview_company_data', 'preview_mode',
                       'preview_email_content', 'preview_email_subject', 'reset_counter']
        for key in preview_keys:
            if key in st.session_state:
                del st.session_state[key]
    
    st.session_state['personalization_mode'] = personalization_mode
    
    if personalization_mode == "🤖 AI-Powered Personalization":
        st.info("🤖 **AI Mode**: Emails will be automatically personalized using your resume content and company research.")
        
        # Default template for AI mode (hidden from user)
        default_template = """Dear [Recruiter Name],

I hope this email finds you well. I am writing to express my interest in opportunities at [Company Name].

Based on my background and experience, I believe I can make a valuable contribution to your team.

I have attached my resume for your review and would welcome the opportunity to discuss how I can contribute to [Company Name]'s continued success.

Thank you for your time and consideration.

Best regards,
[Your Name]"""
        
        email_template = default_template
        
    else:  # Manual Template mode
        st.info("✏️ **Manual Mode**: You will create and edit the email template manually. Use placeholders for personalization.")
        
        # Default template for manual mode
        default_template = """Dear [Recruiter Name],

I hope this email finds you well. I am writing to express my interest in opportunities at [Company Name].

Based on my background and experience, I believe I can make a valuable contribution to your team.

I have attached my resume for your review and would welcome the opportunity to discuss how I can contribute to [Company Name]'s continued success.

Thank you for your time and consideration.

Best regards,
[Your Name]"""
        
        # Template editor (only shown in manual mode)
        email_template = st.text_area(
            "Email Template Structure (AI will personalize this)",
            value=default_template,
            height=200,
            help="Use [Recruiter Name] and [Company Name] as placeholders for personalization"
        )
    
    st.session_state['email_template'] = email_template
    
    # Subject template
    subject_template = st.text_input(
        "Email Subject",
        value="Interest in Opportunities at [Company Name]",
        help="Use [Company Name] and [Recruiter Name] as placeholders"
    )
    
    st.session_state['subject_template'] = subject_template
    
    # Preview section
    if st.button("👁️ Preview Email"):
        if 'company_data' in st.session_state and len(st.session_state['company_data']) > 0:
            sample_row = st.session_state['company_data'].iloc[0]
            company_name = sample_row['Company Name']
            recruiter_name = sample_row['Recruiter']
            
            personalization_mode = st.session_state.get('personalization_mode', '🤖 AI-Powered Personalization')
            
            if personalization_mode == "🤖 AI-Powered Personalization":
                # Extract resume content if available
                resume_summary = ""
                if 'resume_file' in st.session_state:
                    gemini_ai = GeminiAI()
                    resume_summary = gemini_ai.extract_resume_content(st.session_state['resume_file'])
                    st.info(f"📄 Resume content extracted ({len(resume_summary)} characters)")
                
                # Get company data
                company_data = sample_row.to_dict()
                
                # Generate preview using Gemini AI
                gemini_ai = GeminiAI()
                preview_content = gemini_ai.personalize_email(
                    company_name, recruiter_name, email_template, resume_summary, company_data
                )
                
                # Store preview data in session state
                st.session_state['preview_content'] = preview_content
                st.session_state['preview_subject'] = subject_template.replace('[Company Name]', company_name).replace('[Recruiter Name]', recruiter_name)
                st.session_state['preview_company'] = company_name
                st.session_state['preview_recruiter'] = recruiter_name
                st.session_state['preview_email'] = sample_row['Email']
                st.session_state['preview_resume_summary'] = resume_summary
                st.session_state['preview_company_data'] = company_data
                st.session_state['preview_mode'] = 'ai'
                
                st.success("✅ AI preview generated! Scroll down to see and edit the content.")
                    
            else:
                # Manual template mode - store preview data for consistency
                preview_content = email_template.replace("[Company Name]", company_name)
                preview_content = preview_content.replace("[Recruiter Name]", recruiter_name)
                preview_content = preview_content.replace("[COMPANY]", company_name)
                preview_content = preview_content.replace("[RECRUITER]", recruiter_name)
                
                # Store manual preview data in session state
                st.session_state['preview_content'] = preview_content
                st.session_state['preview_subject'] = subject_template.replace('[Company Name]', company_name).replace('[Recruiter Name]', recruiter_name)
                st.session_state['preview_company'] = company_name
                st.session_state['preview_recruiter'] = recruiter_name
                st.session_state['preview_email'] = sample_row['Email']
                st.session_state['preview_mode'] = 'manual'
                
                st.success("✅ Manual template preview generated! Scroll down to see the content.")
        else:
            st.warning("⚠️ Please upload company data first to preview emails")
    
    # Show preview section if preview content exists
    if 'preview_content' in st.session_state:
        preview_mode = st.session_state.get('preview_mode', 'ai')
        
        if preview_mode == 'ai':
            st.subheader("📧 AI-Personalized Email Preview")
            st.write(f"**To:** {st.session_state['preview_email']}")
            
            # Create unique keys that change when reset
            subject_key = f"preview_subject_{st.session_state.get('reset_counter', 0)}"
            body_key = f"preview_body_{st.session_state.get('reset_counter', 0)}"
            
            # Editable subject - show saved version if exists, otherwise original AI content
            subject_value = st.session_state.get('preview_email_subject', st.session_state['preview_subject'])
            edited_subject = st.text_input("**Subject:**", value=subject_value, key=subject_key)
            
            # Editable body - show saved version if exists, otherwise original AI content
            st.write("**Body:**")
            body_value = st.session_state.get('preview_email_content', st.session_state['preview_content'])
            edited_body = st.text_area("", value=body_value, height=200, key=body_key)
            
            # Save edited content option
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📤 Save This Version", key="use_version"):
                    st.session_state['preview_email_content'] = edited_body
                    st.session_state['preview_email_subject'] = edited_subject
                    st.success("✅ This version will be used for the campaign!")
                    st.rerun()
                    
            with col2:
                if st.button("🔄 Reset to AI", key="reset_ai"):
                    # Clear any saved edited versions
                    if 'preview_email_content' in st.session_state:
                        del st.session_state['preview_email_content']
                    if 'preview_email_subject' in st.session_state:
                        del st.session_state['preview_email_subject']
                    # Increment reset counter to force widget refresh
                    st.session_state['reset_counter'] = st.session_state.get('reset_counter', 0) + 1
                    st.success("✅ Reset to AI-generated content!")
                    st.rerun()
            
            # Show resume content preview
            if st.session_state.get('preview_resume_summary'):
                with st.expander("📄 Resume Content Used"):
                    resume_summary = st.session_state['preview_resume_summary']
                    st.text(resume_summary[:500] + "..." if len(resume_summary) > 500 else resume_summary)
                    
            # Show company research
            with st.expander("🏢 Company Research Used"):
                gemini_ai = GeminiAI()
                company_research = gemini_ai.get_company_info(st.session_state['preview_company'])
                st.text(company_research[:500] + "..." if len(company_research) > 500 else company_research)
                
        else:  # manual mode
            st.subheader("📧 Manual Template Email Preview")
            st.write(f"**To:** {st.session_state['preview_email']}")
            st.write(f"**Subject:** {st.session_state['preview_subject']}")
            st.write("**Body:**")
            st.text_area("", value=st.session_state['preview_content'], height=200, disabled=True)

def campaign_settings_section():
    """Campaign settings section"""
    st.subheader("⚙️ Campaign Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        delay_seconds = st.slider(
            "Delay between emails (seconds)",
            min_value=30,
            max_value=600,
            value=60,
            help="Conservative delay to respect Gmail API limits"
        )
        delay_minutes = delay_seconds / 60
    
    st.session_state['delay_minutes'] = delay_minutes
    st.session_state['delay_seconds'] = delay_seconds

def campaign_execution_section():
    """Campaign execution section"""
    st.subheader("🚀 Launch Campaign")
    
    # Check prerequisites
    prerequisites = {
        "Gmail Connected": 'gmail_credentials' in st.session_state,
        "Company Data Uploaded": 'company_data' in st.session_state,
        "Email Template Set": 'email_template' in st.session_state,
        "Resume Uploaded": 'resume_file' in st.session_state,
        "Environment Configured": check_environment()[0]
    }
    
    # Show if edited content is being used
    if 'preview_email_content' in st.session_state:
        st.info("📝 **Using edited email content** from preview. Click 'Reset to AI' to use AI-generated content.")
    
    st.write("**Prerequisites Check:**")
    for prereq, status in prerequisites.items():
        if status:
            st.success(f"✅ {prereq}")
        else:
            st.error(f"❌ {prereq}")
    
    all_ready = all(prerequisites.values())
    
    if all_ready:
        st.success("🎉 Ready to launch campaign!")
        
        if st.button("🚀 Start Email Campaign", type="primary"):
            # Execute campaign
            execute_campaign()
    else:
        st.warning("⚠️ Please complete all prerequisites before launching campaign")

def execute_campaign():
    """Execute the email campaign"""
    st.subheader("📧 Campaign Execution")
    
    # Get campaign data
    company_data = st.session_state['company_data']
    email_template = st.session_state['email_template']
    subject_template = st.session_state['subject_template']
    delay_minutes = st.session_state.get('delay_minutes', 1)
    
    # Initialize email sender
    email_sender = EmailSender()
    
    # Create progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_container = st.empty()
    
    # Execute campaign
    try:
        # Get resume file from session state
        resume_file = st.session_state.get('resume_file')
        resume_path = None
        
        if resume_file:
            # Save uploaded file temporarily with original filename
            import tempfile
            import os
            
            # Create temporary file with original filename
            original_filename = resume_file.name
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'_{original_filename}') as tmp_file:
                tmp_file.write(resume_file.getvalue())
                resume_path = tmp_file.name
        else:
            resume_path = None
            original_filename = None
        
        delay_seconds = st.session_state.get('delay_seconds', 60)
        
        results = email_sender.run_campaign(
            company_data=company_data,
            email_template=email_template,
            subject_template=subject_template,
            resume_path=resume_path,
            resume_name=original_filename,
            delay_seconds=delay_seconds,
            progress_callback=lambda result: update_progress(result, status_text, results_container)
        )
        
        # Clean up temporary file
        if resume_path and os.path.exists(resume_path):
            os.unlink(resume_path)
        
        # Show final results
        summary = email_sender.get_campaign_summary()
        st.success(f"🎉 Campaign completed! Sent: {summary['successful']}/{summary['total']}")
        
        # Store results in session state for download
        st.session_state['campaign_results_data'] = email_sender.campaign_results
        
    except Exception as e:
        st.error(f"❌ Campaign failed: {str(e)}")

def update_progress(result, status_text, results_container):
    """Update progress display"""
    status_text.text(f"Sent to {result['company']}: {'✅' if result['success'] else '❌'}")
    
    # Show recent results
    if 'campaign_results' not in st.session_state:
        st.session_state['campaign_results'] = []
    st.session_state['campaign_results'].append(result)
    
    # Display last 5 results
    recent_results = st.session_state['campaign_results'][-5:]
    results_df = pd.DataFrame(recent_results)
    results_container.dataframe(results_df[['company', 'recruiter', 'success', 'message']])

def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="Cold Email Automation",
        page_icon="📧",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📧 Cold Email Automation")
    st.markdown("---")
    
    # Check environment variables
    env_ok, missing_vars = check_environment()
    
    if not env_ok:
        st.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        st.info("Please check your .env file or environment configuration.")
        st.stop()
    else:
        st.success("✅ All required environment variables are configured!")
    
    # Main application sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔐 Authentication", 
        "📁 Upload Files", 
        "✉️ Email Template", 
        "⚙️ Settings", 
        "🚀 Campaign"
    ])
    
    with tab1:
        gmail_auth_section()
    
    with tab2:
        file_upload_section()
    
    with tab3:
        email_template_section()
    
    with tab4:
        campaign_settings_section()
    
    with tab5:
        campaign_execution_section()
        
        # Download section - only show if campaign results exist
        if 'campaign_results_data' in st.session_state and st.session_state['campaign_results_data']:
            st.markdown("---")
            st.subheader("📥 Download Campaign Results")
            
            # Convert results to CSV
            import pandas as pd
            import io
            
            results_df = pd.DataFrame(st.session_state['campaign_results_data'])
            
            # Convert to CSV string
            csv_buffer = io.StringIO()
            results_df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            
            # Create download button
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f"campaign_results_{timestamp}.csv"
            
            st.download_button(
                label="📥 Download Campaign Results",
                data=csv_data,
                file_name=filename,
                mime="text/csv",
                help="Download the complete campaign results as CSV file"
            )
            
            # Show summary
            summary = {
                'total': len(results_df),
                'successful': len(results_df[results_df['success'] == True]),
                'failed': len(results_df[results_df['success'] == False])
            }
            
            st.info(f"📊 Campaign Summary: {summary['successful']}/{summary['total']} emails sent successfully")

if __name__ == "__main__":
    main()
