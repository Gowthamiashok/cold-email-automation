"""
Gemini AI Integration Module
Handles AI-powered email personalization using free Gemini API
"""

import os
import time
import streamlit as st
import google.generativeai as genai
from typing import Dict, Optional
import PyPDF2
import io
import requests

class GeminiAI:
    """Handles Gemini AI integration for email personalization"""
    
    # Free tier configuration
    MODEL_NAME = "gemini-1.5-flash"  # FREE model
    DAILY_LIMIT = 1500  # requests per day
    RATE_LIMIT = 15     # requests per minute
    DELAY_SECONDS = 4   # Conservative delay between calls
    
    def __init__(self):
        """Initialize Gemini AI client"""
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model = None
        self._setup_client()
    
    def _setup_client(self):
        """Setup Gemini AI client with API key"""
        if not self.api_key:
            st.error("GEMINI_API_KEY not found in environment variables")
            return
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.MODEL_NAME)
            st.success("✅ Gemini AI client initialized successfully")
        except Exception as e:
            st.error(f"Failed to initialize Gemini AI: {str(e)}")
    
    def personalize_email(self, company_name: str, recruiter_name: str, 
                         base_template: str, resume_summary: str = "", 
                         company_data: dict = None) -> str:
        """
        Generate personalized email content using Gemini AI
        
        Args:
            company_name: Name of the target company
            recruiter_name: Name of the recruiter
            base_template: Base email template
            resume_summary: Optional resume summary for personalization
            company_data: Additional company information (role, industry, etc.)
            
        Returns:
            Personalized email content
        """
        if not self.model:
            return self._get_fallback_content(company_name, recruiter_name, base_template)
        
        try:
            # Rate limiting
            time.sleep(self.DELAY_SECONDS)
            
            # Create personalized prompt
            prompt = self._create_personalization_prompt(
                company_name, recruiter_name, base_template, resume_summary, company_data
            )
            
            # Generate content
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return response.text.strip()
            else:
                return self._get_fallback_content(company_name, recruiter_name, base_template)
                
        except Exception as e:
            st.warning(f"AI personalization failed: {str(e)}")
            return self._get_fallback_content(company_name, recruiter_name, base_template)
    
    def _create_personalization_prompt(self, company_name: str, recruiter_name: str, 
                                     base_template: str, resume_summary: str, company_data: dict = None) -> str:
        """Create a detailed prompt for email personalization"""
        
        # Get company information
        company_research = self.get_company_info(company_name)
        
        # Build company context
        company_context = f"**Target Company**: {company_name}"
        company_context += f"\n**Company Research**: {company_research}"
        
        if company_data:
            if 'Role' in company_data:
                company_context += f"\n**Target Role**: {company_data['Role']}"
            if 'Industry' in company_data:
                company_context += f"\n**Industry**: {company_data['Industry']}"
            if 'Company Size' in company_data:
                company_context += f"\n**Company Size**: {company_data['Company Size']}"
        
        # Build resume context
        resume_context = resume_summary if resume_summary else "Resume not provided - use generic professional language"
        
        prompt = f"""
        You are an expert email personalization assistant. Your task is to create a highly personalized cold email outreach based on the candidate's resume and target company information.

        **CANDIDATE PROFILE**:
        {resume_context}

        **TARGET COMPANY INFORMATION**:
        {company_context}
        **Recruiter Name**: {recruiter_name}

        **BASE EMAIL TEMPLATE** (use as structure reference):
        {base_template}

        **PERSONALIZATION REQUIREMENTS**:
        1. **Resume-Based Content**: Extract key skills, experiences, and achievements from the resume and mention specific relevant ones
        2. **Company-Specific Research**: Research {company_name} and mention specific details like:
           - Their core business/services
           - Recent projects or achievements
           - Company culture or values
           - Industry position or reputation
           - Specific technologies they use
        3. **Role Alignment**: If role information is provided, explain how your background aligns with the specific role requirements
        4. **Value Proposition**: Clearly articulate how your skills can benefit {company_name}
        5. **Professional Tone**: Maintain a confident yet humble professional tone
        6. **Concise**: Keep under 200 words while being impactful
        7. **Call-to-Action**: Include a clear next step (call, meeting, etc.)

        **CRITICAL INSTRUCTIONS**:
        - NEVER use placeholder text like [mention...] or [research...]
        - ALWAYS provide specific company details you know about {company_name}
        - Use actual examples from the resume (projects, achievements, skills)
        - Make it sound like you've researched the company thoroughly
        - Avoid generic phrases like "I'm interested in opportunities"
        - Focus on mutual value and fit
        - Use single line breaks between paragraphs
        - Write as if you're genuinely excited about this specific company

        **OUTPUT**: Return only the personalized email content with proper formatting.
        """
        return prompt
    
    def _get_fallback_content(self, company_name: str, recruiter_name: str, 
                            base_template: str) -> str:
        """Generate fallback content when AI fails"""
        # Simple template replacement as fallback
        fallback_content = base_template.replace("[Company Name]", company_name)
        fallback_content = fallback_content.replace("[Recruiter Name]", recruiter_name)
        fallback_content = fallback_content.replace("[COMPANY]", company_name)
        fallback_content = fallback_content.replace("[RECRUITER]", recruiter_name)
        
        # Normalize line breaks - reduce excessive spacing
        fallback_content = fallback_content.replace('\n\n\n', '\n\n')
        
        return fallback_content
    
    def test_connection(self) -> bool:
        """Test Gemini AI connection and API key validity"""
        if not self.model:
            return False
        
        try:
            test_prompt = "Say 'Hello, Gemini AI is working!' in exactly those words."
            response = self.model.generate_content(test_prompt)
            
            if response and response.text:
                return "Hello, Gemini AI is working!" in response.text
            return False
            
        except Exception as e:
            st.error(f"Gemini AI test failed: {str(e)}")
            return False
    
    def get_company_info(self, company_name: str) -> str:
        """
        Get company information for personalization
        
        Args:
            company_name: Name of the company
            
        Returns:
            Company information string
        """
        try:
            # Use Gemini to research the company
            research_prompt = f"""
            Research the company "{company_name}" and provide specific information about:
            1. Core business/services they offer
            2. Recent projects or achievements
            3. Company culture or values
            4. Industry position or reputation
            5. Technologies they use
            6. Any recent news or developments
            
            Provide concise, factual information that would be useful for a job application email.
            Keep it under 300 words.
            """
            
            if self.model:
                response = self.model.generate_content(research_prompt)
                if response and response.text:
                    return response.text.strip()
            
            # Fallback: return basic info
            return f"{company_name} is a company in the industry. They focus on providing quality services and solutions to their clients."
            
        except Exception as e:
            st.warning(f"Company research failed: {str(e)}")
            return f"{company_name} is a company that values innovation and growth."
    
    def extract_resume_content(self, resume_file) -> str:
        """
        Extract text content from uploaded resume PDF
        
        Args:
            resume_file: Uploaded file object from Streamlit
            
        Returns:
            Extracted text content from resume
        """
        try:
            # Read PDF content
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(resume_file.getvalue()))
            
            # Extract text from all pages
            resume_text = ""
            for page in pdf_reader.pages:
                resume_text += page.extract_text() + "\n"
            
            # Clean up the text
            resume_text = resume_text.strip()
            
            # Limit text length to avoid token limits
            if len(resume_text) > 2000:
                resume_text = resume_text[:2000] + "..."
            
            return resume_text
            
        except Exception as e:
            st.warning(f"Failed to extract resume content: {str(e)}")
            return "Resume content extraction failed"
    
    def get_usage_info(self) -> Dict[str, str]:
        """Get information about API usage and limits"""
        return {
            "model": self.MODEL_NAME,
            "daily_limit": f"{self.DAILY_LIMIT:,} requests",
            "rate_limit": f"{self.RATE_LIMIT} requests per minute",
            "delay": f"{self.DELAY_SECONDS} seconds between calls",
            "status": "✅ Free tier active" if self.model else "❌ Not configured"
        }
