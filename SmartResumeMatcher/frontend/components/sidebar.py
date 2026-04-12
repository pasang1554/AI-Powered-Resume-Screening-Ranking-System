import streamlit as st
import os
from frontend.utils.constants import SAMPLE_JD, SAMPLE_RESUME_1, SAMPLE_RESUME_2, SAMPLE_RESUME_3

def render_sidebar():
    with st.sidebar:
        try:
            # Replaced hardcoded path with a more flexible one or a fallback
            st.image("https://raw.githubusercontent.com/pasang1554/AI-Powered-Resume-Screening-Ranking-System/main/logo.png", width='stretch')
        except:
            st.markdown("### 🤖 ResumeAI")
        
        st.markdown(
            """<div style="text-align: center; margin-top: -15px; margin-bottom: 25px;">
            <h1 style="font-size: 22px; font-weight: 800; color: white; margin: 0; letter-spacing: -0.5px; font-family: 'Outfit';">ResumeAI</h1>
            <p style="color: #64748B; font-size: 10px; margin-top: 2px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em;">Institutional Intelligence</p>
            </div>""",
            unsafe_allow_html=True,
        )
        
        st.markdown("---")
        if st.session_state.get("token") is not None:
            st.success("✅ Authenticated")
            st.markdown("---")
            st.markdown("#### 🎭 Strategic Context")
            intelligence_role = st.segmented_control("Active Persona", ["Operator", "Architect", "Strategist"], default="Operator")
            
            if st.button("Logout", width='stretch'):
                st.session_state.token = None
                st.rerun()
            st.markdown("---")
            return intelligence_role

        if st.button("🚀 Load Sample Data", width='stretch'):
            st.session_state.demo_loaded = True
            st.session_state.demo_jd = SAMPLE_JD
            st.session_state.demo_resumes = [
                ("John_Smith.txt", SAMPLE_RESUME_1),
                ("Sara_Johnson.txt", SAMPLE_RESUME_2),
                ("Mike_Chen.txt", SAMPLE_RESUME_3),
            ]
            st.rerun()
            
        if st.session_state.get("demo_loaded"):
            st.success("✅ Demo loaded!")
            
        st.markdown("---")
        threshold = st.slider("Match Threshold", 0, 100, 50)
        
        st.markdown("### 🎯 Skill Prioritization")
        priority_skills = st.multiselect(
            "Select Priority Skills (5x Weight)",
            options=["Python", "SQL", "React", "Docker", "Kubernetes", "AWS", "Machine Learning", "Communication"],
            help="Selected skills will be given 5x more importance in the final match score calculation."
        )
        st.session_state.priority_skills = priority_skills

        st.markdown("---")
        st.markdown("### 🔐 Neural Safeguards")
        blind_hiring = st.toggle("🔒 Blind Hiring Mode", value=False, help="Anonymize candidate names and PII during initial screening to eliminate unconscious bias.")

        st.markdown("---")
        st.markdown("### 🤖 Groq AI Settings")
        groq_api_key = st.text_input("Groq API Key (Optional for Llama 3)", value=os.getenv("GROQ_API_KEY", ""), type="password", help="Enter your Groq API key to enable qualitative AI analysis of resumes.")
        
        st.markdown("---")
        st.markdown(
            """<div style="text-align: center; color: rgba(255,255,255,0.4); font-size: 11px; margin-top: 20px; font-weight: 500;">
            Institutional Talent Singularity v1.1.0<br>
            <span style="color: #6366F1;">●</span> Secure Neural Core Active
            </div>""",
            unsafe_allow_html=True,
        )
        
        return {
            "threshold": threshold,
            "blind_hiring": blind_hiring,
            "groq_api_key": groq_api_key,
            "priority_skills": priority_skills
        }
