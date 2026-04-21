"""
Smart Resume Matcher - AI-Powered Recruitment Intelligence Ecosystem
Modular Enterprise Edition
"""

import streamlit as st
import os
import requests
import io
import time
from dotenv import load_dotenv

# Import components
from frontend.components.sidebar import render_sidebar
from frontend.components.auth import render_auth_ui
from frontend.components.pipeline import render_talent_pipeline
from frontend.components.history import render_history_view
from frontend.components.dashboard import render_analysis_dashboard
from frontend.components.interviews import render_interview_manager
from frontend.components.public_portal import render_public_career_portal
from frontend.components.analytics_view import render_institutional_insights
from frontend.utils.constants import SAMPLE_JD

# Load environment variables
load_dotenv()

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")

# Schema Guard: Ensure API_URL has a scheme (important for Render Blueprints)
if API_URL and not API_URL.startswith(("http://", "https://")):
    # Default to https for external hosts, but permit http for internal ones
    if "onrender.com" in API_URL or "." in API_URL.split("/")[0]:
        API_URL = f"https://{API_URL}"
    else:
        API_URL = f"http://{API_URL}"

# Debug: This will show up in Render's dashboard logs for the dashboard service
print(f"DEBUG: Connecting to Backend at: {API_URL}")

st.set_page_config(
    page_title="Smart Resume Matcher",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Inject external CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("frontend/assets/style.css")

# Session State Initialization
if "token" not in st.session_state:
    st.session_state.token = None
if "results" not in st.session_state:
    st.session_state.results = None
if "job_desc_input" not in st.session_state:
    st.session_state.job_desc_input = ""
if "nav_selection" not in st.session_state:
    st.session_state.nav_selection = "🔍 New Analysis"
if "focus_candidate_name" not in st.session_state:
    st.session_state.focus_candidate_name = None

# --- SIDEBAR ---
sidebar_data = render_sidebar()
intelligence_role = sidebar_data if isinstance(sidebar_data, str) else "Operator"

# --- MAIN UI ---
if not st.session_state.token:
    if "entry_mode" not in st.session_state:
        st.session_state.entry_mode = None

    if st.session_state.entry_mode is None:
        st.markdown(
            """<div style='text-align: center; padding: 4rem 0;'>
                <h1 style='font-size: 3.5rem; font-weight: 900; margin-bottom: 3rem; background: linear-gradient(90deg, #6366F1, #EC4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
                    Neural Talent Singularity
                </h1>
                <p style='color: #94A3B8; font-size: 1.2rem; max-width: 600px; margin: 0 auto 4rem auto;'>Select your portal to begin. The future of institutional talent discovery is here.</p>
            </div>""", unsafe_allow_html=True
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(
                """<div class="job-card" style="text-align: center; cursor: pointer; height: 350px; display: flex; flex-direction: column; justify-content: center;">
                    <h2 style="font-size: 2rem; color: #EC4899;">🌍 Public Portal</h2>
                    <p style="color: #94A3B8; margin: 1.5rem 0;">Explore global clusters, discover your match, and apply autonomously.</p>
                </div>""", unsafe_allow_html=True
            )
            if st.button("🚀 Explore Opportunities", width='stretch', key="enter_public"):
                st.session_state.entry_mode = "Public"
                st.rerun()

        with col2:
            st.markdown(
                """<div class="modern-card" style="text-align: center; cursor: pointer; height: 350px; display: flex; flex-direction: column; justify-content: center; padding: 2rem;">
                    <h2 style="font-size: 2rem; color: #6366F1;">🏛️ Institutional</h2>
                    <p style="color: #94A3B8; margin: 1.5rem 0;">Manage pipelines, run deep neural audits, and orchestrate talent.</p>
                </div>""", unsafe_allow_html=True
            )
            if st.button("🔑 Recruiter Admin Login", width='stretch', key="enter_recruiter"):
                st.session_state.entry_mode = "Recruiter"
                st.rerun()
        
        st.stop()

    if st.session_state.entry_mode == "Public":
        if st.button("⬅️ Switch to Institutional Login", type="secondary"):
            st.session_state.entry_mode = None
            st.rerun()
        render_public_career_portal(API_URL)
        st.stop()
    
    # Recruiter-specific Landing (Login)
    if st.button("⬅️ Back to Portal Selection", type="secondary"):
        st.session_state.entry_mode = None
        st.rerun()

    st.markdown(
        """<div class="hero-v7">
            <h1>Institutional<br>Talent Discovery</h1>
            <p>Enterprise-grade candidate mapping powered by verified semantic intelligence and neural ranking systems.</p>
        </div>""",
        unsafe_allow_html=True,
    )
    render_auth_ui(API_URL)
    st.stop()

# Auth Header
auth_header = {"Authorization": f"Bearer {st.session_state.token}"}

# Navigation Layout
st.sidebar.markdown('<p class="nav-header">Intelligence Suite</p>', unsafe_allow_html=True)

# Determine index for radio selector
nav_options = ["🔍 New Analysis", "🗄️ Database History", "🚀 Talent Pipeline", "🤝 Interview Manager", "📊 Institutional Insights"]
nav_index = nav_options.index(st.session_state.nav_selection) if st.session_state.nav_selection in nav_options else 0

nav_mode = st.sidebar.radio(
    "Navigation", 
    nav_options, 
    index=nav_index,
    label_visibility="collapsed",
    key="nav_radio"
)
st.session_state.nav_selection = nav_mode

if nav_mode == "🗄️ Database History":
    groq_key = sidebar_data.get("groq_api_key") if isinstance(sidebar_data, dict) else ""
    render_history_view(API_URL, auth_header, groq_key)

elif nav_mode == "🚀 Talent Pipeline":
    import pandas as pd
    if st.session_state.results:
        df = pd.DataFrame(st.session_state.results)
        render_talent_pipeline(df, auth_header, API_URL)
    else:
        st.info("Run an analysis first to populate the pipeline.")

elif nav_mode == "🤝 Interview Manager":
    render_interview_manager(API_URL, auth_header)

elif nav_mode == "📊 Institutional Insights":
    groq_key = sidebar_data.get("groq_api_key") if isinstance(sidebar_data, dict) else ""
    render_institutional_insights(API_URL, auth_header, groq_key)

elif nav_mode == "🔍 New Analysis":
    col_jd, col_resumes = st.columns(2)
    with col_jd:
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.markdown("### 📋 Job Architecture")
        job_description = st.text_area(
            "Job Description", 
            value=st.session_state.get("job_desc_input", ""), 
            height=250, 
            label_visibility="collapsed", 
            placeholder="Enter job requirements..."
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col_resumes:
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.markdown("### 📄 Talent Pipeline")
        uploaded_files = st.file_uploader(
            "Upload Resumes (PDF/TXT)", type=["pdf", "txt"], accept_multiple_files=True, label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🔍 Analyze Candidates", type="primary", width='stretch'):
        if not job_description or (not uploaded_files and not st.session_state.get("demo_loaded")):
            st.error("⚠️ Please provide a job description and upload resumes.")
        else:
            with st.spinner("Processing intelligence..."):
                files_payload = []
                if st.session_state.get("demo_loaded"):
                    from frontend.utils.constants import SAMPLE_RESUME_1, SAMPLE_RESUME_2, SAMPLE_RESUME_3
                    files_payload.append(("files", ("John_Smith.txt", io.BytesIO(SAMPLE_RESUME_1.encode()), "text/plain")))
                    files_payload.append(("files", ("Sara_Johnson.txt", io.BytesIO(SAMPLE_RESUME_2.encode()), "text/plain")))
                else:
                    for f in uploaded_files:
                        files_payload.append(("files", (f.name, f.read(), f.type)))
                
                payload = {
                    "job_description": job_description,
                    "threshold": sidebar_data.get("threshold", 50) if isinstance(sidebar_data, dict) else 50,
                    "blind_hiring": sidebar_data.get("blind_hiring", False) if isinstance(sidebar_data, dict) else False,
                    "groq_api_key": sidebar_data.get("groq_api_key", "") if isinstance(sidebar_data, dict) else "",
                }
                
                try:
                    res = requests.post(f"{API_URL}/analyze/pdf", data=payload, files=files_payload, headers=auth_header)
                    if res.status_code == 200:
                        st.session_state.results = res.json().get("candidates", [])
                        st.session_state.job_desc_input = job_description
                        st.success("Analysis Complete!")
                        st.rerun()
                    else: st.error(f"Analysis failed: {res.text}")
                except Exception as e: st.error(f"Connection error (URL: {API_URL}): {e}")

    if st.session_state.results:
        render_analysis_dashboard(
            st.session_state.results, 
            job_description, 
            sidebar_data, 
            API_URL, 
            auth_header
        )
