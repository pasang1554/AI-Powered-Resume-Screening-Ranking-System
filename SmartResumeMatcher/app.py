"""
Universal Talent Singularity - AI-Powered Recruitment Intelligence Ecosystem
Version 8.1.13 - Final Enterprise Release
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime
import requests
import io
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SAMPLE_JD = """SOFTWARE ENGINEER
Full Stack Development Position

LOCATION: Bangalore, India
EXPERIENCE: 3-6 Years
SALARY: 8-15 LPA

JOB SUMMARY:
We are looking for a skilled Software Engineer with experience in full stack development.

REQUIRED SKILLS:
- Python programming (3+ years)
- JavaScript and React framework experience
- Node.js backend development
- SQL and PostgreSQL databases
- Docker containerization
- AWS cloud platform
- Git version control
- Agile development methodology

EXPERIENCE REQUIREMENTS:
- Minimum 3 years of software development experience
- Experience building RESTful APIs
- Knowledge of microservices architecture
"""

SAMPLE_RESUME_1 = """JOHN SMITH
Senior Software Engineer
Email: john.smith@email.com | Phone: +1-555-0123

SUMMARY
Experienced software engineer with 6 years in full stack development.

SKILLS
- Python, Django, FastAPI - 6 years
- JavaScript, React, TypeScript - 5 years
- Node.js, Express backend - 4 years
- PostgreSQL, MySQL, MongoDB - 5 years
- AWS cloud platform - 3 years
- Docker and Kubernetes - 2 years
- Git, CI/CD, Agile methodology

EXPERIENCE

Senior Software Engineer | TechCorp Inc.
2020 - Present (4 years)
- Led microservices architecture for 1M+ users
- Built RESTful APIs handling 50K requests/second
- Implemented CI/CD pipelines

Software Engineer | StartupXYZ
2018 - 2020 (2 years)
- Built e-commerce APIs
- Tech Stack: Node.js, Express, MongoDB

EDUCATION
B.Tech in Computer Science
State University, 2018
"""

SAMPLE_RESUME_2 = """SARA JOHNSON
Full Stack Developer
Email: sara.j@email.com

SUMMARY
Passionate developer with 4 years of experience.

SKILLS
- JavaScript, React, Next.js - 4 years
- Node.js, Express - 3 years
- Python, Django - 1 year
- PostgreSQL, MySQL - 3 years
- Git, Docker basics
- Agile methodology

EXPERIENCE

Full Stack Developer | WebSolutions Co.
2019 - Present (5 years)
- Developed e-commerce platform
- Created React UI components
- Built RESTful APIs

EDUCATION
B.Sc in Information Technology
University, 2018
"""

SAMPLE_RESUME_3 = """MIKE CHEN
Junior Python Developer
Email: mike.c@email.com

SUMMARY
Recent graduate eager to start career.

SKILLS
- Python basics
- Flask web framework
- HTML, CSS
- SQL basics
- Git basics

EXPERIENCE
No formal work experience - fresh graduate

EDUCATION
B.Tech in Computer Science
New Institute, 2024
"""

st.set_page_config(
    page_title="Universal Talent Singularity",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "demo_loaded" not in st.session_state:
    st.session_state.demo_loaded = False
if "results" not in st.session_state:
    st.session_state.results = None
if "job_desc_input" not in st.session_state:
    st.session_state.job_desc_input = ""
if "last_jd_id" not in st.session_state:
    st.session_state.last_jd_id = None

@st.fragment
def render_talent_pipeline(df, auth_header, API_URL):
    st.markdown("Monitor and manage candidate progression through the recruitment lifecycle.")
    stages = ["Shortlisted", "Interviewing", "Offer Extended", "Hired", "Not Selected"]
    cols = st.columns(len(stages))
    for i, stage in enumerate(stages):
        with cols[i]:
            st.markdown(f"**{stage}**")
            stage_candidates = df[df["Status"] == stage]
            if stage_candidates.empty and stage == "Shortlisted":
                 stage_candidates = df[df["Status"] == "Shortlisted"]
            
            for _, sc in stage_candidates.iterrows():
                with st.expander(f"{sc['Candidate']} ({sc['Score']}%)"):
                    new_status = st.selectbox("Update Stage", stages, index=stages.index(stage), key=f"pipe_status_{sc['id']}")
                    if st.button("Update", key=f"pipe_btn_{sc['id']}"):
                        p_res = requests.patch(f"{API_URL}/analyses/{sc.get('id')}/status", json={"status": new_status}, headers=auth_header)
                        if p_res.status_code == 200:
                            # State Sync: Update local results to reflect change
                            if st.session_state.results:
                                for res_item in st.session_state.results:
                                    if res_item.get("id") == sc.get("id"):
                                        res_item["Status"] = new_status
                            st.success("Updated")
                            time.sleep(0.5)
                            st.rerun(scope="fragment")
                        else: st.error("Failed to update status")

def extract_semantic_skills(text):
    """Simple utility to extract likely skills from text for visualization."""
    if not text: return []
    # Basic keyword extraction as fallback
    keywords = ["Python", "JavaScript", "React", "Node", "SQL", "Docker", "AWS", "Git", "Java", "C++", "C#", "Go", "Rust", "Swift", "Machine Learning", "AI", "Cloud", "Agile"]
    found = [k for k in keywords if k.lower() in text.lower()]
    return found
if "token" not in st.session_state:
    st.session_state.token = None

API_URL = "http://localhost:8000/api/v1"

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Outfit:wght@500;600;700;800;900&display=swap');

:root {
    --primary: #6366f1;
    --primary-hover: #4f46e5;
    --bg-main: #020617;
    --text-main: #F8FAFC;
    --text-dim: #94A3B8;
    --border: rgba(255, 255, 255, 0.08);
}

.stApp {
    background: radial-gradient(circle at 50% -20%, #1e1b4b, #020617);
    color: var(--text-main);
    font-family: 'Plus Jakarta Sans', sans-serif;
}

#MainMenu, footer { visibility: hidden; }

/* Institutional Card v2 */
.modern-card {
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(20px);
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 3rem;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

/* Hero v7.2 */
.hero-v7 h1 {
    font-family: 'Outfit', sans-serif;
    font-size: 5rem;
    font-weight: 900;
    letter-spacing: -0.05em;
    background: linear-gradient(135deg, #FFF 0%, #6366F1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Premium Inputs v7.2 */
.stTextInput > div > div > input, .stTextArea > div > div > textarea {
    background: rgba(2, 6, 23, 0.8) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: white !important;
    padding: 1rem !important;
    font-size: 1rem !important;
}

.stTextInput > div > div > input:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
}

/* Button & Tabs v7.2 */
.stButton > button {
    background: var(--primary) !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-family: 'Outfit', sans-serif !important;
    letter-spacing: 0.01em !important;
    height: 3.2rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.stButton > button:hover {
    background: var(--primary-hover) !important;
    transform: scale(1.02) !important;
}

.stTabs [data-baseweb="tab-list"] { 
    background: rgba(255,255,255,0.03); 
    border-radius: 12px;
    padding: 4px;
    margin-bottom: 24px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: var(--text-dim);
    transition: all 0.2s ease;
}
.stTabs [aria-selected="true"] {
    background: rgba(255,255,255,0.05) !important;
    color: white !important;
}

/* METRICS v7.2 */
.top-metric {
    background: rgba(255,255,255,0.02);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 2.5rem;
}
</style>
""",
    unsafe_allow_html=True,
)


with st.sidebar:
    try:
        # Using the locally generated institutional logo
        st.image("/Users/stanzinpasang/.gemini/antigravity/brain/2197f38e-ca1b-4875-8e87-6335862a1648/resumeai_institutional_logo_1775799900397.png", width='stretch')
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
    if st.session_state.token is not None:
        st.success("✅ Authenticated")
        
        # Phase 14: Role-Adaptive UI Context Selector
        st.markdown("---")
        st.markdown("#### 🎭 Strategic Context")
        intelligence_role = st.segmented_control("Active Persona", ["Operator", "Architect", "Strategist"], default="Operator")
        
        if st.button("Logout", width='stretch'):
            st.session_state.token = None
            st.rerun()
        st.markdown("---")

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
    
    # Feature 2: Weighted Skill Analysis UI
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
        """<div style="text-align: center; color: rgba(255,255,255,0.3); font-size: 10px; margin-top: 20px;">
        ResumeAI Pro v5.1<br>Fullstack API Powered
        </div>""",
        unsafe_allow_html=True,
    )

st.markdown(
    """<div class="hero-v7">
        <h1>Institutional<br>Talent Discovery</h1>
        <p>Enterprise-grade candidate mapping powered by verified semantic intelligence and neural ranking systems.</p>
    </div>""",
    unsafe_allow_html=True,
)

if not st.session_state.token:
    st.markdown(
        """<div style="text-align: center; padding: 4rem 0 2rem 0;">
            <h2 style="font-family: 'Outfit'; font-size: 3rem; font-weight: 900; margin-bottom: 0.5rem; background: linear-gradient(to right, #FFF, #6366F1); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Secure Access</h2>
            <p style="color: #64748B; font-size: 1.1rem;">Enterprise Recruitment Intelligence Portal</p>
        </div>""", 
        unsafe_allow_html=True
    )
    
    # Custom Login Card Container
    login_container = st.container()
    with login_container:
        st.markdown('<div class="modern-card" style="max-width: 480px; margin: 0 auto;">', unsafe_allow_html=True)
        # Replaced st.info with a custom styled div
        st.markdown(
            """<div style="background: rgba(79, 70, 229, 0.1); border: 1px solid rgba(79, 70, 229, 0.2); border-radius: 12px; padding: 1rem; margin-bottom: 2rem; color: #A5B4FC; font-size: 0.9rem; text-align: center;">
                🔑 Access: <b>test@example.com</b> | <b>admin123</b>
            </div>""",
            unsafe_allow_html=True
        )
        
        auth_tab1, auth_tab2 = st.tabs(["Login", "Register"])
    
    with auth_tab1:
        login_email = st.text_input("Email", value="test@example.com", key="login_email")
        login_password = st.text_input("Password", value="test@example.com", type="password", key="login_pw")
        if st.button("Login", width='stretch'):
            try:
                res = requests.post(f"{API_URL}/token", data={"username": login_email, "password": login_password})
                if res.status_code == 200:
                    st.session_state.token = res.json()["access_token"]
                    # Fetch User Info
                    u_res = requests.get(f"{API_URL}/me", headers={"Authorization": f"Bearer {st.session_state.token}"})
                    if u_res.status_code == 200:
                        st.session_state.user_obj = u_res.json()
                    st.success("✅ Logged in!")
                    st.rerun()
                else:
                    if res.status_code >= 500:
                       st.error(f"⚠️ Backend crashed (Status {res.status_code}). Please RESTART YOUR TERMINALS! Error: {res.text}")
                    else:
                       st.error("⚠️ Invalid credentials")
            except requests.exceptions.ConnectionError:
                st.error("⚠️ Cannot connect to backend (is it running?)")
    
    with auth_tab2:
        reg_email = st.text_input("Email", key="reg_email")
        reg_username = st.text_input("Username", key="reg_user")
        reg_password = st.text_input("Password", type="password", key="reg_pw")
        if st.button("Register", width='stretch'):
            try:
                res = requests.post(f"{API_URL}/register", json={"email": reg_email, "username": reg_username, "password": reg_password})
                if res.status_code == 200:
                    st.success("✅ Registered! Please login.")
                else:
                    try:
                        error_detail = res.json().get('detail', 'Registration failed')
                    except:
                        error_detail = f"Server Error ({res.status_code}): {res.text}"
                    st.error(f"⚠️ {error_detail}")
            except requests.exceptions.ConnectionError:
                st.error("⚠️ Cannot connect to backend (is it running?)")
    st.stop()

st.sidebar.markdown("---")
# Display User Role
if st.session_state.get("user_obj"):
    u = st.session_state.user_obj
    st.sidebar.markdown(f"""
    <div style="background: rgba(99,102,241,0.15); border: 1px solid rgba(99,102,241,0.3); border-radius: 12px; padding: 12px; text-align: center; margin-bottom: 20px;">
        <div style="font-size: 10px; text-transform: uppercase; color: #a5b4fc; letter-spacing: 1px;">Authenticated Role</div>
        <div style="font-size: 18px; font-weight: 700; color: #fff;">🛡️ {u.get('role', 'User')}</div>
        <div style="font-size: 12px; color: rgba(255,255,255,0.4);">{u.get('email')}</div>
    </div>
    <div style="background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.2); border-radius: 8px; padding: 8px; text-align: center; margin-bottom: 10px;">
        <div style="font-size: 9px; color: #10b981; font-weight: 700;">🌌 SYSTEM STATUS: ONLINE</div>
        <div style="font-size: 10px; color: rgba(255,255,255,0.5);">v8.1.13 | Enterprise Node</div>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown('<p class="nav-header">Intelligence Suite</p>', unsafe_allow_html=True)
nav_options = ["🔍 New Analysis", "🗄️ Database History"]
if intelligence_role in ["Architect", "Strategist"]:
    nav_options.append("🧠 Talent Intelligence")
if intelligence_role == "Strategist":
    nav_options.append("🔮 Singularity Foresight")
nav_options.append("🔬 Details")

nav_mode = st.sidebar.radio("Navigation", nav_options, label_visibility="collapsed")

st.sidebar.markdown('<p class="nav-header">Strategic Nexus</p>', unsafe_allow_html=True)
nexus_options = ["🛡️ Resilience Hub"]
if intelligence_role == "Strategist":
    nexus_options.extend(["🔮 AI Foresight", "🌌 The Singularity", "🤝 Human-AI Synergy", "⚖️ Global Sovereignty"])

nexus_mode = st.sidebar.selectbox("Nexus", nexus_options, label_visibility="collapsed")

if nexus_mode != "🛡️ Resilience Hub":
    nav_mode = nexus_mode

if nav_mode == "🗄️ Database History":
    st.markdown("### 🗄️ Recruitment Intelligence Pool")
    st.markdown("Advanced filtering and historical intelligence retrieved directly from the secure candidate vault.")
    
    # Restoration Logic
    def load_project_to_dashboard(jd_id):
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        try:
            # 1. Fetch JD Text
            jd_res = requests.get(f"{API_URL}/job-descriptions", headers=headers)
            if jd_res.status_code == 200:
                jds = jd_res.json()
                target_jd = next((j for j in jds if j['id'] == jd_id), None)
                if target_jd:
                    st.session_state.job_desc_input = target_jd.get('content', target_jd.get('text', ''))
            
            # 2. Fetch Candidates for this JD
            cand_res = requests.get(f"{API_URL}/job-descriptions/{jd_id}/analyses", headers=headers)
            if cand_res.status_code == 200:
                raw_results = cand_res.json()
                
                # Map DB schema to UI schema
                ui_results = []
                for r in raw_results:
                    ui_results.append({
                        "id": r.get("id"),
                        "Candidate": r.get("candidate_name"),
                        "Score": r.get("match_score"),
                        "ATS": r.get("ats_score"),
                        "Status": r.get("status"),
                        "Experience": r.get("experience_years"),
                        "Skills_Count": r.get("skills_found"),
                        "Missing_Count": r.get("missing_skills_count"),
                        "AI_Evaluation": r.get("ai_evaluation"),
                        "Radar_Data": r.get("radar_data"),
                        "filename": r.get("resume_filename"),
                        "resume_text": r.get("resume_text", ""), # Required for AI Simulation
                        "created_at": r.get("created_at")
                    })
                
                st.session_state.results = ui_results
                st.session_state.last_jd_id = jd_id
                st.success(f"✅ Project {jd_id} restored successfully!")
                time.sleep(1)
                st.rerun()
        except Exception as e:
            st.error(f"Restoration failed: {e}")

    # Advanced Filtering Bar
    filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])
    with filter_col1:
        search_name = st.text_input("🔍 Search Candidate Name", placeholder="Enter name to filter...", key="hist_search")
    with filter_col2:
        status_filter = st.selectbox("Status", ["All", "Shortlisted", "Not Selected"], key="hist_status")
    with filter_col3:
        min_score_filter = st.slider("Min Score", 0, 100, 0, key="hist_score")
        
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        params = {}
        if status_filter != "All":
            params["status"] = status_filter
        if min_score_filter > 0:
            params["min_score"] = float(min_score_filter)
            
        res = requests.get(f"{API_URL}/analyses", headers=headers, params=params)
        if res.status_code == 200:
            history_data = res.json()
            if history_data:
                # Local client-side search for name
                if search_name:
                    history_data = [a for a in history_data if search_name.lower() in a["candidate_name"].lower()]
                
                if history_data:
                    df_hist = pd.DataFrame(history_data)
                    
                    st.markdown("---")
                    st.markdown("#### ⚡ Strategic Health Index")
                    h_col1, h_col2, h_col3 = st.columns(3)
                    with h_col1:
                        avg_vel = round(df_hist['match_score'].count() / 7, 1) # Mock velocity calculation
                        st.metric("Pipeline Velocity", f"{avg_vel} cand/wk", delta="12%")
                    with h_col2:
                        avg_q = round(df_hist['match_score'].mean(), 1)
                        st.metric("Quality of Hire Index", f"{avg_q}%", delta="5%")
                    with h_col3:
                        conv_rate = round((len(df_hist[df_hist['status'] == 'Shortlisted']) / len(df_hist) * 100), 1) if not df_hist.empty else 0
                        st.metric("Strategic Yield", f"{conv_rate}%")
                    
                    hist_tab1, hist_tab2, hist_tab3 = st.tabs(["📁 Project Vault", "📜 Compliance Audit Logs", "💎 Global Talent Vault"])
                    
                    with hist_tab1:
                        # Projects Management Section
                        st.markdown("#### Managed Recruitment Projects")
                    unique_jds = df_hist.groupby('job_description_id').agg({
                        'created_at': 'max',
                        'candidate_name': 'count'
                    }).sort_values('created_at', ascending=False)
                    
                    for jd_id, info in unique_jds.iterrows():
                        p_col1, p_col2, p_col3 = st.columns([2, 1, 1])
                        with p_col1:
                            st.write(f"**Project ID: {jd_id}** (Analyzed: {str(info['created_at'])[:16]})")
                        with p_col2:
                            st.write(f"👥 {info['candidate_name']} Candidates")
                        with p_col3:
                            if st.button(f"🔌 Restore to Dashboard", key=f"restore_{jd_id}", width='stretch'):
                                load_project_to_dashboard(jd_id)
                        
                        # Phase 6: AI Strategic Synthesis
                        synth_col1, synth_col2 = st.columns([1, 4])
                        with synth_col1:
                            if st.button("🪄 Synthesis", key=f"synth_jd_{jd_id}", width='stretch', help="Analyze top performers to synthesize the 'Ideal Profile'."):
                                with st.spinner("Synthesizing..."):
                                    s_res = requests.post(f"{API_URL}/analytics/project/{jd_id}/synthesis", data={"groq_api_key": groq_api_key}, headers=headers)
                                    if s_res.status_code == 200:
                                        st.session_state[f"synth_{jd_id}"] = s_res.json()["synthesis"]
                                    else: st.error("Synthesis failed.")
                        
                        if f"synth_{jd_id}" in st.session_state:
                            with synth_col2:
                                st.info(f"**🧠 Strategic Synthesis:** {st.session_state[f'synth_{jd_id}'][:200]}...")
                                if st.button("Read Full Synthesis", key=f"full_synth_{jd_id}"):
                                    st.write(st.session_state[f"synth_{jd_id}"])

                    with hist_tab2:
                        st.markdown("#### System-Wide Compliance Audit")
                        audit_res = requests.get(f"{API_URL}/audit-logs", headers=headers)
                        if audit_res.status_code == 200:
                            audits = audit_res.json()
                            if audits:
                                df_audit = pd.DataFrame(audits)
                                st.dataframe(df_audit[['created_at', 'module', 'action', 'details']], width='stretch', hide_index=True)
                            else:
                                st.info("No audit logs recorded yet.")

                        else:
                            st.error("Failed to load audit logs.")

                    # Phase 6: Public Gateway connectivity
                    st.markdown("---")
                    st.markdown("#### 🚀 Public Gateway Connectivity")
                    st.code(f"POST {API_URL}/public/apply/{{JD_ID}}", language="bash")
                    st.caption("Integrate this endpoint into your public careers page. Required fields: name, email, file (resume).")

                    with hist_tab3:
                        st.markdown("#### Strategic Talent Pool")
                        st.markdown("A unified view of all unique candidates ever evaluated by the system.")
                        vault_res = requests.get(f"{API_URL}/candidates/vault", headers=headers)
                        if vault_res.status_code == 200:
                            vault_cands = vault_res.json()
                            if vault_cands:
                                vdf = pd.DataFrame(vault_cands)
                                st.dataframe(vdf[["name", "email", "skills", "created_at"]], width='stretch', hide_index=True)
                            else:
                                st.info("Talent vault is currently empty.")
                        else:
                            st.error("Failed to load talent vault.")
                    
                    st.markdown("---")
                    st.markdown("#### ⏱️ Detailed Historical Records")
                    if 'created_at' in df_hist.columns:
                        df_hist['created_at'] = pd.to_datetime(df_hist['created_at']).dt.strftime('%Y-%m-%d %H:%M')
                    
                    # Reorder columns for better UX
                    cols = [c for c in ['id', 'candidate_name', 'match_score', 'status', 'created_at'] if c in df_hist.columns]
                    st.dataframe(df_hist[cols], width='stretch', hide_index=True)
                    
                    # Bulk Export Section
                    st.markdown("#### 📦 Strategic Bulk Export")
                    export_jds = df_hist['job_description_id'].unique()
                    export_col1, export_col2 = st.columns([2, 1])
                    with export_col1:
                        target_jd = st.selectbox("Select Project for ZIP Export", export_jds, format_func=lambda x: f"Project ID: {x}")
                    with export_col2:
                        state_key = f"zip_ready_{target_jd}"
                        if st.button("🚀 Prepare Shortlisted Resumes (ZIP)", width='stretch'):
                            with st.spinner("Packaging intelligence vault..."):
                                try:
                                    exp_res = requests.get(f"{API_URL}/job-descriptions/{target_jd}/export", headers=headers)
                                    if exp_res.status_code == 200:
                                        st.session_state[state_key] = exp_res.content
                                    else:
                                        st.error(f"Failed to export: {exp_res.text}")
                                except Exception as e:
                                    st.error(f"Export Error: {e}")
                        
                        if state_key in st.session_state:
                            st.download_button(
                                label="📥 Click to Save ZIP Archive",
                                data=st.session_state[state_key],
                                file_name=f"Shortlisted_Support_{target_jd}.zip",
                                mime="application/zip",
                                width='stretch'
                            )
                else:
                    st.info("No candidates match your current search filters.")
            else:
                st.info("No past analyses found in the database. Run a new analysis first.")
                
            st.markdown("---")
            if st.button("🗑️ Wipe Entire Database History", type="primary", width='stretch', help="Securely clears all database history for this account."):
                try:
                    del_res = requests.delete(f"{API_URL}/analyses/reset", headers={"Authorization": f"Bearer {st.session_state.token}"})
                    if del_res.status_code == 200:
                        st.success("✅ " + del_res.json().get("message", "Database Wiped"))
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"Failed to manually wipe database: {del_res.text}")
                except Exception as e:
                    st.error(f"Connection Error: {e}")
        else:
            st.error(f"Failed to load history from backend: {res.text}")
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")

elif nav_mode == "🔍 New Analysis":
    col_jd, col_resumes = st.columns(2)
    with col_jd:
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.markdown("### 📋 Job Architecture")
        jd_tools = st.columns([1.5, 1])
        with jd_tools[1]:
            jd_action = st.selectbox("AI Mode", ["Optimizer", "Generator"], label_visibility="collapsed")
            if jd_action == "Optimizer":
                if st.button("✨ Optimize"):
                    if not groq_api_key: st.error("API Key Required")
                    else:
                        with st.spinner("Refining..."):
                            o_res = requests.post(f"{API_URL}/analyze/jd/optimize", data={"content": st.session_state.get("job_desc_input", ""), "groq_api_key": groq_api_key}, headers={"Authorization": f"Bearer {st.session_state.token}"})
                            if o_res.status_code == 200:
                                st.session_state.job_desc_input = o_res.json()["optimized"]
                                st.rerun()
            else:
                with st.popover("Draft New"):
                    jd_title = st.text_input("Role")
                    jd_key = st.text_area("Key Req")
                    if st.button("🪄 Script"):
                        with st.spinner("Generating..."):
                            g_res = requests.post(f"{API_URL}/analyze/jd/generate", data={"title": jd_title, "key_points": jd_key, "groq_api_key": groq_api_key}, headers={"Authorization": f"Bearer {st.session_state.token}"})
                            if g_res.status_code == 200:
                                st.session_state.job_desc_input = g_res.json()["generated"]
                                st.rerun()

        job_description = st.text_area(
            "Job Description", value=st.session_state.get("job_desc_input", ""), height=180, label_visibility="collapsed", placeholder="Enter official requirements..."
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col_resumes:
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.markdown("### 📄 Talent Pipeline")
        st.markdown("<p style='font-size: 0.9rem; color: #64748B; margin-bottom: 1.5rem;'>Upload formal resumes for institutional neural mapping.</p>", unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "PDF/TXT", type=["pdf", "txt"], accept_multiple_files=True, label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔍 Analyze Candidates", type="primary", width='stretch'):
            if st.session_state.get("demo_loaded") and st.session_state.get("demo_jd"):
                job_desc = st.session_state.demo_jd
                files_to_upload = st.session_state.demo_resumes
            elif job_description and uploaded_files:
                job_desc = job_description
                files_to_upload = uploaded_files
            else:
                st.error("⚠️ Load demo or enter JD + upload resumes")
                st.stop()

            with st.spinner("Analyzing securely via API..."):
                progress = st.progress(0)
                
                # Prepare multipart payload
                files_payload = []
                if st.session_state.get("demo_loaded"):
                    for name, text in files_to_upload:
                        b = io.BytesIO(text.encode('utf-8'))
                        files_payload.append(("files", (name, b, "text/plain")))
                else:
                    for f in files_to_upload:
                        f.seek(0)
                        files_payload.append(("files", (f.name, f.read(), f.type)))
                        
                data = {
                    "job_description": job_desc, 
                    "threshold": threshold, 
                    "groq_api_key": groq_api_key,
                    "weighted_skills": st.session_state.get("priority_skills", []),
                    "blind_hiring": blind_hiring
                }
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                progress.progress(0.3)
                
                try:
                    response = requests.post(f"{API_URL}/analyze/pdf", data=data, files=files_payload, headers=headers)
                    progress.progress(0.9)
                    if response.status_code == 200:
                        results = response.json().get("candidates", [])
                        if blind_hiring:
                            import hashlib
                            for r in results:
                                r["Real_Name"] = r.get("Real_Name", r["Candidate"]) 
                                name_hash = hashlib.md5(r["Real_Name"].encode()).hexdigest()[:6].upper()
                                r["Candidate"] = f"Candidate UID-{name_hash}"
                        st.session_state.results = results
                        st.session_state.job_desc_input = job_desc
                    else: st.error(f"API Error {response.status_code}")
                    progress.progress(1.0)
                except Exception as e: st.error(f"Execution failed: {e}")
            st.rerun()

    if st.session_state.results:
        results = st.session_state.results
        df = pd.DataFrame(results)
        st.markdown("### 📊 Recruitment Intelligence Dashboard")
            
        # 1. KPI Strategy Banner
        kpi_cols = st.columns(5)
        metrics = [
            (len(df), "Total Candidates", "gradient"),
            (len(df[df["Status"] == "Shortlisted"]), "Shortlisted", "green"),
            (f"{df['Score'].mean():.0f}%", "Avg Match", "gradient"),
            (f"{df['ATS'].mean():.0f}%", "Avg ATS", "gradient"),
            (f"{df['Experience'].mean():.1f}yr", "Avg Exp", "gradient"),
        ]
        for col, (val, label, color) in zip(kpi_cols, metrics):
            with col:
                st.markdown(
                    f"""<div class="top-metric">
                        <div class="label">{label}</div>
                        <div class="value">{val}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

        # 2. Main Dashboard Navigation
        tab1, tab2, tab3, tab4, tab_pipe, tab_int, tab5 = st.tabs(
            ["🏆 Rankings", "📈 Analytics", "⚖️ Comparison", "🔬 Details", "🏗️ Pipeline", "📅 Interviews", "💾 Export"]
        )

        with tab1:
            st.markdown("### 🏆 Top Talent Rankings")
            selected_comparison = st.multiselect(
                "⚖️ Select Candidates for Side-by-Side Comparison (Max 3)",
                options=df["Candidate"].tolist(),
                max_selections=3,
                key="global_cand_select"
            )
            st.session_state.selected_comparison = selected_comparison
            
            if len(df) >= 3:
                p_cols = st.columns(3)
                for i, (emoji, color) in enumerate(zip(["🥇", "🥈", "🥉"], ["#fbbf24", "#94a3b8", "#b45309"])):
                    with p_cols[i]:
                        c = df.iloc[i]
                        st.markdown(
                            f"""<div class="podium-card"><div style="font-size: 40px;">{emoji}</div><div style="font-weight: 700; color: #fff;">{c["Candidate"]}</div><div style="font-size: 28px; font-weight: 800; color: {color};">{c["Score"]}%</div></div>""",
                            unsafe_allow_html=True
                        )
            st.markdown("---")
            st.dataframe(df[["Rank", "Candidate", "Score", "ATS", "Experience", "Status"]], width='stretch', hide_index=True)

        with tab2:
            st.markdown("### 📊 Talent Strategy Analytics")
            
            # Feature 3: Global Analytics Fetch
            st.markdown("#### 🌍 Global Recruitment Suite Intelligence")
            auth_header = {"Authorization": f"Bearer {st.session_state.token}"}
            try:
                g_res = requests.get(f"{API_URL}/analyses", headers=auth_header)
                if g_res.status_code == 200:
                    gall = g_res.json()
                    if gall:
                        gdf = pd.DataFrame(gall)
                        g1, g2, g3 = st.columns(3)
                        g1.metric("Total Talent Managed", len(gdf))
                        g2.metric("Shortlisted Globally", len(gdf[gdf['status'] == 'Shortlisted']))
                        g3.metric("Global Avg Fit Score", f"{gdf['match_score'].mean():.1f}%")
            except Exception as g_err:
                st.warning("⚠️ Global Talent Suite benchmarks temporarily unavailable.")
            
            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1:
                st.write("**Candidate Score Distribution**")
                st.bar_chart(df.set_index("Candidate")["Score"])
            with c2:
                st.write("**Application Status Breakdown**")
                st.write(df["Status"].value_counts())
            
            # Market Gap Graph
            all_missing = []
            for m in df["Missing"]:
                if isinstance(m, list): all_missing.extend(m)
            if all_missing:
                from collections import Counter
                counts = Counter(all_missing).most_common(10)
                sdf = pd.DataFrame(counts, columns=["Skill", "Count"])
                st.write("**Top 10 Skill Gaps in Current Pool**")
                st.bar_chart(sdf.set_index("Skill")["Count"])
            
            # STRATEGIC DASHBOARD FEATURES
            st.markdown("---")
            st.markdown("### 🏆 Strategic Talent Intelligence")
            
            s1, s2 = st.columns(2)
            with s1:
                st.write("**Skill Supply vs Demand Heatmap**")
                req_skills = extract_semantic_skills(st.session_state.job_desc_input)
                found_skills_list = []
                for s in df["Top_Skills"]: found_skills_list.extend(s)
                
                demand_counts = Counter([s for s in found_skills_list if s in req_skills])
                supply_counts = Counter([s for s in found_skills_list if s not in req_skills])
                
                heat_df = pd.DataFrame([
                    {"Skill": s, "Type": "Demand Match", "Count": count} for s, count in demand_counts.items()
                ] + [
                    {"Skill": s, "Type": "Market Supply", "Count": count} for s, count in supply_counts.items()
                ])
                if not heat_df.empty:
                    fig = px.density_heatmap(heat_df, x="Skill", y="Type", z="Count", color_continuous_scale="Viridis")
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                else: st.info("Not enough data for heatmap")

            with s2:
                st.write("**Experience Seniority Mix**")
                fig = px.pie(df, names="Experience", values="Score", hole=0.4, color_discrete_sequence=px.colors.sequential.PuBu)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        with tab3:
            st.markdown("### ⚖️ Intelligence Comparison View")
            
            # Feature: Direct Selection in Comparison Tab
            sel = st.multiselect(
                "Select Candidates for Deep Side-by-Side Analysis",
                options=df["Candidate"].tolist(),
                default=st.session_state.get("selected_comparison", []),
                max_selections=3,
                key="direct_tab_comp_select"
            )
            st.session_state.selected_comparison = sel
            
            if not sel:
                st.info("💡 Select candidates from the dropdown above or in the **🏆 Rankings** tab to compare them side-by-side.")

            else:
                cdf = df[df["Candidate"].isin(sel)]
                comp_cols = st.columns(len(cdf))
                for i, (_, r) in enumerate(cdf.iterrows()):
                    with comp_cols[i]:
                        # Elite Candidate Card Header
                        st.markdown(f"""
                        <div style="background: rgba(99, 102, 241, 0.1); border-left: 4px solid #6366f1; border-radius: 8px; padding: 16px; margin-bottom: 20px;">
                            <div style="font-size: 10px; text-transform: uppercase; color: #a5b4fc; font-weight: 700; letter-spacing: 1px; margin-bottom: 4px;">Candidate Identifier</div>
                            <div style="font-size: 20px; font-weight: 800; color: white; font-family: 'Outfit';">{r['Candidate']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                        m1, m2 = st.columns(2)
                        with m1:
                            st.metric("Score", f"{r['Score']}%")
                        with m2:
                            st.metric("ATS", f"{r['ATS']}%")
                        
                        st.markdown(f"""
                        <div style="background: rgba(255,255,255,0.03); border-radius: 8px; padding: 12px; font-size: 13px; color: #94a3b8; border: 1px solid rgba(255,255,255,0.05);">
                            <b>AI Verdict:</b> {r['AI_Evaluation'].get('recommendation', 'N/A')}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if r.get("Radar_Data"):
                            st.markdown("<br>", unsafe_allow_html=True)
                            fig = go.Figure()
                            fig.add_trace(go.Scatterpolar(r=r['Radar_Data']['candidate'], theta=r['Radar_Data']['categories'], fill='toself', line=dict(color='#6366f1')))
                            fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 100]), bgcolor="rgba(0,0,0,0)"), height=250, margin=dict(l=20,r=20,t=20,b=20), showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key=f"comp_radar_{i}_{r['id']}")

        with tab4:
            st.markdown("### 🔬 Deep Candidate Intelligence")
            for _, row in df.iterrows():
                with st.expander(f"#{row['Rank']} {row['Candidate']} - {row['Score']}% Intelligence Profile"):
                    # Phase 6: Skill Gap Visualizer
                    st.markdown("#### 🎯 Skill Gap Analysis")
                    # Check for missing skills in the row data
                    # In some parts of app.py we use 'Missing_Count', we should use the actual list if available
                    # Assuming the backend returns 'missing_skills'
                    missing = row.get('missing_skills', [])
                    if missing:
                        st.error(f"⚠️ Critical Skill Gaps: {', '.join(missing)}")
                    else:
                        st.success("✅ Full Skill Alignment")

                    m1, m2, m3 = st.columns(3)
                    m1.metric("Match Score", f"{row['Score']}%")
                    m2.metric("ATS Score", f"{row['ATS']}%")
                    m3.metric("Experience", f"{row['Experience']} Yrs")
                    
                    st.write(f"**AI Summary:** {row['AI_Evaluation'].get('summary', 'N/A')}")
                    
                    # Radar Chart Mapping
                    if row.get("Radar_Data"):
                        st.markdown("---")
                        st.write("**📊 Skill Proficiency Mapping**")
                        fig = go.Figure()
                        fig.add_trace(go.Scatterpolar(r=row['Radar_Data']['job_description'], theta=row['Radar_Data']['categories'], fill='toself', name='JD Requirements'))
                        fig.add_trace(go.Scatterpolar(r=row['Radar_Data']['candidate'], theta=row['Radar_Data']['categories'], fill='toself', name='Candidate Proficiency'))
                        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=400)
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key=f"det_radar_{row['id']}")

                    # Interview Scheduling Logic
                    st.markdown("---")
                    st.markdown("#### 📅 Schedule Performance Interview")
                    with st.form(key=f"sked_form_{row['id']}"):
                        i_date = st.date_input("Interview Date")
                        i_time = st.time_input("Preferred Time")
                        i_medium = st.selectbox("Platform", ["Google Meet", "Zoom", "Slack", "Physical Office"])
                        i_notes = st.text_area("Notes for Interviewer")
                        if st.form_submit_button("🚀 Finalize & Notify"):
                            i_dt = datetime.combine(i_date, i_time).isoformat()
                            payload = {"candidate_id": row['candidate_id'], "interview_date": i_dt, "medium": i_medium, "notes": i_notes}
                            res = requests.post(f"{API_URL}/interviews", json=payload, headers=auth_header)
                            if res.status_code == 200:
                                st.success("✅ Interview Synchronized")
                                # Feature 6: Mock Email Dispatch
                                notify_payload = {
                                    "candidate_name": row['Candidate'],
                                    "score": row['Score'],
                                    "role": st.session_state.job_desc_input.split('\n')[0] if st.session_state.job_desc_input else "Strategic Individual",
                                    "candidate_email": row.get('Email'),
                                    "real_name": row.get('Real_Name')
                                }
                                n_res = requests.post(f"{API_URL}/notify", json=notify_payload, headers=auth_header)
                                if n_res.status_code == 200:
                                    st.info("📬 Recruitment dispatch active...")
                                    # Actually call the Phase 7 Email Orchestration Service
                                    email_body = f"Dear {row['Candidate']},\n\nWe are excited to invite you to an interview for the position. Your strategic score: {row['Score']}%.\n\nBest regards,\nRecruitment Team"
                                    email_data = {
                                        "to_email": row.get('Email', 'candidate@example.com'),
                                        "subject": "Interview Invitation - Strategic Recruitment Pool",
                                        "body": email_body
                                    }
                                    e_dispatch = requests.post(f"{API_URL}/emails/send", data=email_data, headers=auth_header)
                                    if e_dispatch.status_code == 200:
                                        st.success("📧 Invitation Orchestrated via Secure Gateway")
                                        st.code(f"To: {email_data['to_email']}\nSubject: {email_data['subject']}\n\n{email_body}", language="text")
                                    else:
                                        st.warning("⚠️ Email delivery mock failed, check gateway logs.")
                            else: st.error("Failed to sync interview")

                    # Operational Tools
                    st.markdown("---")
                    colA, colB = st.columns(2)
                    with colA:
                        if st.button(f"📥 Download Prepared Resume", key=f"dl_resum_{row['candidate_id']}"):
                            res = requests.get(f"{API_URL}/candidates/{row['candidate_id']}/resume", headers=auth_header)
                            if res.status_code == 200:
                                st.download_button("Click to Download", res.content, file_name=f"resume_{row['candidate_id']}.pdf")
                    with colB:
                        if st.button(f"📄 Generate Intelligence Report (PDF)", key=f"gen_rep_{row['id']}"):
                            from reportlab.lib.pagesizes import letter
                            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
                            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                            from reportlab.lib import colors
                            import io
                            buffer = io.BytesIO()
                            doc = SimpleDocTemplate(buffer, pagesize=letter)
                            styles = getSampleStyleSheet()
                            title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor("#6366f1"), alignment=1)
                            elements = [Paragraph("AI Candidate Intelligence Report", title_style), Spacer(1, 20)]
                            t_data = [["Name:", row['Candidate']], ["Score:", f"{row['Score']}%"], ["Status:", row['Status']]]
                            t = Table(t_data, colWidths=[150, 300])
                            t.setStyle(TableStyle([('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#f3f4f6")), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)]))
                            elements.append(t)
                            doc.build(elements)
                            st.download_button("📥 Download PDF Report", buffer.getvalue(), file_name=f"{row['Candidate']}_Report.pdf", width='stretch')
                    # Feature 5: AI Coaching Hub
                    st.markdown("---")
                    st.markdown("#### 🧠 AI-Powered ATS Coaching")
                    if st.button("🚀 Generate Precision Coaching Report", key=f"coach_btn_{row['id']}"):
                        with st.spinner("Decoding JD-Resume alignment..."):
                            coach_payload = {
                                "job_description": st.session_state.job_desc_input,
                                "resume_text": row['text'],
                                "groq_api_key": groq_api_key
                            }
                            c_res = requests.post(f"{API_URL}/analyze/coach", data=coach_payload, headers=auth_header)
                            if c_res.status_code == 200:
                                coach_data = c_res.json()
                                st.success("✅ Intelligence Report Generated")
                                st.write(f"**Overall Feedback:** {coach_data.get('overall_feedback')}")
                                
                                c1, c2 = st.columns(2)
                                with c1:
                                    st.write("**⚠️ Critical Fixes**")
                                    for fix in coach_data.get('critical_fixes', []): st.warning(fix)
                                with c2:
                                    st.write("**💡 Suggested Additions**")
                                    for add in coach_data.get('suggested_additions', []): st.info(add)
                                
                                st.write("**📑 Impact Statements (Rewrite Examples)**")
                                for imp in coach_data.get('impact_statements', []):
                                    st.code(imp, language="text")
                            else:
                                st.error("Failed to reach coaching engine. Check Groq API Key.")

        with tab_pipe:
            st.markdown("### 🏗️ Interactive Talent Pipeline")
            render_talent_pipeline(df, auth_header, API_URL)

        with tab_int:
            st.markdown("### 📅 Central Recruitment Calendar")
            
            # Feature 7: Automated Scorecard Generation
            st.markdown("#### 📋 AI-Generated Interview scorecard")
            if st.button("🪄 Generate Dynamic Strategic Scorecard", help="Creates a personalized evaluation rubric based on the JD."):
                if not groq_api_key: st.error("Groq API Key Required")
                else:
                    with st.spinner("Synthesizing evaluation criteria..."):
                        s_res = requests.post(f"{API_URL}/analyze/scorecard", data={"job_description": st.session_state.job_desc_input, "groq_api_key": groq_api_key}, headers=auth_header)
                        if s_res.status_code == 200:
                            scorecard = s_res.json()
                            st.success("✅ Scorecard Architecture Finalized")
                            st.write(f"**Interviewer Notes:** {scorecard.get('overall_scorecard_notes')}")
                            
                            for crit in scorecard.get('evaluation_criteria', []):
                                with st.expander(f"Criteria: {crit['category']} (Weight: {crit['weight']})"):
                                    st.write("**Key Questions:**")
                                    for q in crit['key_questions']: st.write(f"- {q}")
                                    st.write("**Look For:**")
                                    for l in crit['look_for']: st.write(f"- {l}")
                            
                            st.write("**🧠 Behavioral Foundations**")
                            for bq in scorecard.get('behavioral_questions', []): st.write(f"- {bq}")
                        else: st.error("Scorecard generation failed.")
            

            st.markdown("---")

            st.markdown("#### 🤖 Autonomous Candidate Simulator (Prep Mode)")
            selected_cand_sim = st.selectbox("Target Candidate for Roleplay", df['Candidate'].tolist() if not df.empty else [])
            sim_question = st.text_input("Interviewer Question", placeholder="Ask anything to test the candidate...")
            if st.button("🎙️ Start AI Simulation"):
                if not groq_api_key: 
                    st.error("🔑 Groq API Key required for AI Simulation. Please enter it in the sidebar.")
                elif not st.session_state.get('job_desc_input'):
                    st.error("📋 Job Description context missing. Please analyze a project or restore one from history.")
                elif not sim_question.strip():
                    st.warning("❓ Please enter a question for the candidate to answer.")
                else:
                    target_data = next((r for r in df.to_dict('records') if r['Candidate'] == selected_cand_sim), None)
                    if target_data:
                        with st.spinner(f"🤖 AI Candidate {selected_cand_sim} is thinking..."):
                            # Logic Fix: Use raw resume text instead of AI Evaluation dictionary
                            raw_resume = target_data.get('text', target_data.get('resume_text', 'Standard background'))
                            
                            sim_payload = {
                                "resume_text": str(raw_resume),
                                "job_description": st.session_state.job_desc_input,
                                "question": sim_question,
                                "groq_api_key": groq_api_key
                            }
                            
                            try:
                                sim_res = requests.post(f"{API_URL}/analyze/simulate", data=sim_payload, headers=auth_header)
                                if sim_res.status_code == 200:
                                    st.markdown(f"**AI Candidate Response:**\n\n{sim_res.json()['response']}")
                                elif sim_res.status_code == 422:
                                    st.error(f"❌ Simulation Data Validation Failed (422). Details: {sim_res.text}")
                                else: 
                                    st.error(f"❌ Simulation failed (Status {sim_res.status_code}). Check API connectivity.")
                            except Exception as e:
                                st.error(f"⚠️ Connection error during simulation: {e}")



            try:
                i_res = requests.get(f"{API_URL}/interviews", headers=auth_header)
                if i_res.status_code == 200:
                    interviews = i_res.json()
                    if interviews:
                        idf = pd.DataFrame(interviews)
                        all_res = st.session_state.get("results", [])
                        name_map = {r['id']: r['Candidate'] for r in all_res}
                        idf['Candidate'] = idf['candidate_id'].map(name_map).fillna("Candidate")
                        st.markdown("#### 📅 Calendar Orchestration")
                        idf_display = idf.copy()
                        # Apply premium formatting to display dataframe
                        idf_display['status'] = idf_display['status'].apply(lambda s: f"🟢 {s}" if s == "Passed" else (f"🔴 {s}" if s == "Failed" else f"⚪ {s}"))
                        st.dataframe(idf_display[["Candidate", "interview_date", "medium", "status", "notes"]], width='stretch', hide_index=True)
                        
                        sync_col1, sync_col2 = st.columns([2, 1])
                        with sync_col1:
                            target_ics = st.selectbox("Select Interview for Calendar Sync", idf['id'].tolist(), format_func=lambda x: f"Interview {x}", key="ics_sel")
                        with sync_col2:
                            if st.button("📥 Download iCal (.ics)", width='stretch'):
                                ics_res = requests.get(f"{API_URL}/interviews/{target_ics}/ics", headers=auth_header)
                                if ics_res.status_code == 200:
                                    st.download_button("Save Invite", ics_res.content, f"interview_{target_ics}.ics", "text/calendar", width='stretch')
                                else: st.error("Sync failed")
        
                        st.markdown("---")
                        st.markdown("#### 📝 Record Interview Feedback")
                        target_int = st.selectbox("Select Interview to Update", idf['id'].tolist(), format_func=lambda x: f"Interview {x}")
                        with st.form(key="feedback_form"):
                            f_score = st.slider("Interviewer Score", 0.0, 10.0, 5.0)
                            f_status = st.selectbox("Decision", ["Pending", "Passed", "Failed"])
                            f_summary = st.text_area("Feedback Summary")
                            if st.form_submit_button("💾 Save Feedback"):
                                f_payload = {
                                    "interviewer_score": f_score,
                                    "feedback_summary": f_summary,
                                    "status": f_status
                                }
                                # Using patch endpoint
                                f_res = requests.patch(f"{API_URL}/interviews/{target_int}/feedback", data=f_payload, headers=auth_header)
                                if f_res.status_code == 200:
                                    st.success("✅ Feedback Saved")
                                    st.rerun()
                                else: st.error("Failed to save feedback")
                    
                        st.markdown("---")
                        st.markdown("#### 🧠 AI Strategic Feedback Synthesis")
                        if st.button("🪄 Synthesize Final Candidate Verdict", key="syn_btn", type="secondary"):
                            if not groq_api_key: st.error("Groq API Key Required")
                            else:
                                with st.spinner("Analyzing cross-round feedback patterns..."):
                                    # Select a candidate from the current results to synthesize
                                    target_cand_id = idf['candidate_id'].iloc[0] # For demo, take the first one or let user pick
                                    s_res = requests.post(f"{API_URL}/interviews/synthesis/{target_cand_id}", data={"groq_api_key": groq_api_key}, headers=auth_header)
                                    if s_res.status_code == 200:
                                        verdict = s_res.json()
                                        st.success(f"✅ Final Verdict Synthesized for {verdict.get('candidate')}")
                                        st.markdown(verdict.get('synthesis'))
                                        if "results" in st.session_state:
                                            for res_item in st.session_state.results:
                                                if res_item.get("Candidate") == verdict.get('candidate'):
                                                    res_item["AI_Evaluation"] = verdict.get('synthesis')
                                    else: st.error("Synthesis failed. Ensure feedback is recorded for rounds.")
                    else: st.info("No interviews scheduled yet.")
            except Exception as e:
                st.warning(f"⚠️ Intelligence Layer Synchronization: {str(e)}")


        with tab5:
            st.markdown("### 💾 Project Persistence & Export")
            
            e1, e2 = st.columns(2)
            with e1:
                st.download_button("📥 Export Project Stats (CSV)", df.to_csv(index=False), "recruitment_intelligence.csv", "text/csv", width='stretch')
                st.download_button("📄 Export Project Schema (JSON)", df.to_json(orient="records"), "recruitment_intelligence.json", "application/json", width='stretch')
            
            with e2:
                if st.button("🏆 Generate Enterprise Recruitment Brief (PDF)", width='stretch'):
                    if 'last_jd_id' in st.session_state:
                        with st.spinner("Compiling project intelligence..."):
                            b_res = requests.get(f"{API_URL}/analyze/project/{st.session_state.last_jd_id}/brief", headers=auth_header)
                            if b_res.status_code == 200:
                                st.download_button("Download Brief PDF", b_res.content, f"recruitment_brief_{st.session_state.last_jd_id}.pdf", width='stretch')
                            elif b_res.status_code == 404:
                                st.error("❌ Project data not found. Ensure the project is saved and analyze candidates first.")
                            else:
                                err_msg = b_res.json().get('detail', 'Unknown error')
                                st.error(f"⚠️ Intelligence Compilation Failed: {err_msg}")
                    else:
                        st.warning("Save or Restore a project first to generate a brief.")
                
                st.markdown("---")
                st.markdown("#### 🏁 Project Closure")
                if st.button("🏆 Finalize Hire & Archive Project", width='stretch', type="primary"):
                    if 'last_jd_id' in st.session_state:
                        with st.spinner("Closing recruitment loop..."):
                            a_res = requests.post(f"{API_URL}/job-descriptions/{st.session_state.last_jd_id}/archive", headers=auth_header)
                            if a_res.status_code == 200:
                                st.success("✅ Talent Secured & Project Archived")
                                st.balloons()
                                time.sleep(1)
                                # Reset dashboard state
                                st.session_state.results = []
                                st.session_state.last_jd_id = None
                                st.rerun()
                            else: st.error("Archiving failed.")
                    else:
                        st.warning("No active project to archive.")
    else:
        st.error("No candidates matched or backend returned empty results.")

elif nav_mode == "🧠 Talent Intelligence":
    st.markdown("### 🧠 Strategic Talent Intelligence")
    st.markdown("Aggregated insights from across the entire organization's talent vault.")
    
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    s_res = requests.get(f"{API_URL}/analytics/skills", headers=headers)
    
    if s_res.status_code == 200:
        skill_counts = s_res.json()
        if skill_counts:
            sdf = pd.DataFrame(list(skill_counts.items()), columns=["Skill", "Frequency"]).sort_values("Frequency", ascending=False)
            
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown("#### 📊 Global Skill Distribution")
                st.bar_chart(sdf.set_index("Skill"), color="#6366f1")
            
            with c2:
                st.markdown("#### 🏆 Rare & Critical Skills")
                st.dataframe(sdf, width='stretch', hide_index=True)
                
            st.markdown("---")
            st.markdown("#### 🌐 Talent Vault Composition")
            v_res = requests.get(f"{API_URL}/candidates/vault", headers=headers)
            if v_res.status_code == 200:
                vault = v_res.json()
                st.metric("Total Unique Talent Profiles", len(vault))
            
            st.markdown("---")
            st.markdown("#### 🌎 Market Scarcity Benchmarking")
            st.markdown("AI-powered analysis of your Talent Vault against industry-wide scarcity markers.")
            
            m_res = requests.get(f"{API_URL}/analytics/market-scarcity", headers=headers)
            if m_res.status_code == 200:
                benchmarks = m_res.json()
                bdf = pd.DataFrame(benchmarks)
                
                fig_mkt = px.bar(
                    bdf, 
                    x="scarcity_index", 
                    y="skill", 
                    orientation='h',
                    color="difficulty",
                    color_discrete_map={"Critical": "#ef4444", "High": "#f59e0b", "Moderate": "#10b981"},
                    title="Skill Scarcity Index (Higher = Harder to Hire)",
                    labels={"scarcity_index": "Scarcity Index (%)", "skill": "Core Skill"}
                )
                fig_mkt.update_layout(height=400, showlegend=True)
                st.plotly_chart(fig_mkt, use_container_width=True, config={'displayModeBar': False})
                
                st.write("**Strategic Intelligence Verdict:**")
                critical_skills = [b['skill'] for b in benchmarks if b['difficulty'] == "Critical"]
                if critical_skills:
                    st.warning(f"🚨 **Action Required:** The following skills are critically scarce in your current pool: {', '.join(critical_skills)}. Consider adjusting JD requirements or targeted headhunting.")
                else:
                    st.success("✅ **Market Stability:** Your Talent Vault currently has a healthy reach across critical industry skillsets.")
        else:
            st.info("Insufficient data for talent intelligence visualization.")
    else:
        st.error("Failed to retrieve skill analytics.")


elif nav_mode == "🔮 Singularity Foresight":
    st.markdown("### 🔮 Universal Talent Singularity Foresight")
    st.markdown("Autonomous organizational continuity and quantum workforce trajectory analysis.")
    
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    s_col1, s_col2 = st.columns(2)
    
    with s_col1:
        st.markdown("#### 🛡️ Autonomous Succession Regents")
        st.info("Continuous monitoring of leadership readiness across the Talent Vault.")
        
        if 'last_jd_id' in st.session_state and st.session_state.last_jd_id:
            suc_res = requests.get(f"{API_URL}/analytics/succession-regent/{st.session_state.last_jd_id}", headers=headers)
            if suc_res.status_code == 200:
                sdata = suc_res.json()
                st.markdown(f"""
                <div style="background: rgba(99,102,241,0.1); border: 2px solid #6366f1; border-radius: 12px; padding: 25px;">
                    <div style="font-size: 14px; color: #a5b4fc; font-weight: 700;">SUCCESSION STRENGTH</div>
                    <div style="font-size: 32px; font-weight: 900; color: #fff;">{sdata['succession_strength']}</div>
                    <div style="font-size: 18px; color: #10b981; font-weight: 600; margin-top: 10px;">Primary: {sdata['primary_successor']}</div>
                    <div style="font-size: 12px; color: #94a3b8; margin-top: 5px;">{sdata['regent_action']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("##### 🛤️ Continuity Roadmap")
                for road in sdata['bridge_training_roadmap']:
                    col_r1, col_r2 = st.columns([2, 1])
                    col_r1.write(f"**{road['skill']}**")
                    col_r2.info(f"{road['status']} ({road['eta']})")
            else: st.warning("Succession intelligence requires an active project context.")
        else: st.info("Select or Restore a project to enable succession foresight.")

    with s_col2:
        st.markdown("#### 🌌 Quantum Workforce Simulator")
        st.info("5-Year Trajectory Analysis: Efficiency, Retention, and Market Arbitrage.")
        
        q_res = requests.get(f"{API_URL}/analytics/quantum-simulator", headers=headers)
        if q_res.status_code == 200:
            qdata = q_res.json()
            st.metric("Simulation Confidence", qdata['simulation_confidence'])
            st.success(f"🚀 {qdata['velocity_impact']}")
            st.markdown(f"""
            <div style="background: rgba(16,185,129,0.05); border: 1px solid rgba(16,185,129,0.2); border-radius: 12px; padding: 15px;">
                <div style="font-weight: 700; color: #10b981;">FINANCIAL NPV IMPACT</div>
                <div style="font-size: 24px; font-weight: 800;">{qdata['financial_roi']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("##### ⚠️ Risk Pockets Detected")
            for risk in qdata['risk_pockets']:
                st.error(risk)
        else: st.error("Quantum simulation engine disconnected.")
        
    st.markdown("---")
    st.markdown("#### ⚛️ Kinetic Talent Cluster Visualization (3D)")
    # Generate 3D Talent Clusters from Vault
    v_res = requests.get(f"{API_URL}/candidates/vault", headers=headers)
    if v_res.status_code == 200:
        vault = v_res.json()
        if len(vault) > 2:
            import numpy as np
            vdf = pd.DataFrame(vault)
            # Mock 3D coordinates for visualization
            vdf['x'] = np.random.rand(len(vdf)) * 100
            vdf['y'] = np.random.rand(len(vdf)) * 100
            vdf['z'] = np.random.rand(len(vdf)) * 100
            
            fig_3d = px.scatter_3d(
                vdf, x='x', y='y', z='z', 
                color='skills', 
                hover_name='name',
                title="Global Talent Singularity Clusters",
                template="plotly_dark",
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            fig_3d.update_layout(height=600, margin=dict(l=0, r=0, b=0, t=0))
            st.plotly_chart(fig_3d, use_container_width=True, config={'displayModeBar': False})
        else:
             st.info("Aggregate more talent data to enable 3D kinetic clustering.")
    st.markdown("### 🛡️ Enterprise Infrastructure Resilience Hub")
    st.markdown("Monitor system health, run stress tests, and manage disaster recovery protocols.")
    
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    # 1. Real-Time Telemetry
    st.markdown("#### 📊 Real-Time System Telemetry")
    t_res = requests.get(f"{API_URL}/system/telemetry", headers=headers)
    if t_res.status_code == 200:
        telemetry = t_res.json()
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("API Latency", f"{telemetry['api_response_time_ms']}ms", delta="-5ms")
        m2.metric("AI Inference", f"{telemetry['ai_inference_latency_ms']}ms")
        m3.metric("DB Health", telemetry['database_health'])
        m4.metric("Active Load", f"{telemetry['active_connections']} conn")
        
        # Health Gauges
        c1, c2 = st.columns(2)
        with c1:
            fig_mem = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = telemetry['memory_usage_percent'],
                title = {'text': "Memory Usage %"},
                gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#6366f1"}}
            ))
            fig_mem.update_layout(height=250, margin=dict(l=20,r=20,t=40,b=20))
            st.plotly_chart(fig_mem, use_container_width=True, config={'displayModeBar': False})
            
        with c2:
            st.markdown(f"""
            <div style="background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3); border-radius: 12px; padding: 20px; height: 180px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                <div style="color: #10b981; font-size: 14px; font-weight: 600;">UPTIME STATUS</div>
                <div style="color: #fff; font-size: 32px; font-weight: 800;">{telemetry['uptime_days']} Days</div>
                <div style="color: rgba(255,255,255,0.4); font-size: 11px;">Continuous Enterprise Availability</div>
            </div>
            """, unsafe_allow_html=True)
            
    # 2. Disaster Recovery
    st.markdown("---")
    st.markdown("#### 💾 Disaster Recovery & State Persistence")
    b1, b2 = st.columns(2)
    with b1:
        if st.button("🏁 Generate Full System Backup", width='stretch'):
            with st.spinner("Encrypting systems state..."):
                b_res = requests.post(f"{API_URL}/system/backup", headers=headers)
                if b_res.status_code == 200:
                    st.success("✅ Backup Persistent Layer Created")
                    st.json(b_res.json()["data"])
                else: st.error("Backup failed.")
    with b2:
        st.file_uploader("Restore System from State", type=["json"], help="Upload a previous backup to restore the Talent Vault.")

    # 3. Stress Testing
    st.markdown("---")
    st.markdown("#### 🚀 Enterprise Stress Test Simulation")
    st.markdown("Test the stability of your high-concurrency async engine.")
    load_count = st.slider("Simulated Resume Influx", 10, 500, 50)
    if st.button("🔥 Launch Stress Test Simulation", width='stretch', type="primary"):
        with st.spinner(f"Flooding engine with {load_count} requests..."):
            s_res = requests.post(f"{API_URL}/system/stress-test", data={"resume_count": load_count}, headers=headers)
            if s_res.status_code == 200:
                stress_data = s_res.json()
                st.success(f"✅ System Result: {stress_data['system_health']}")
                st.write(f"Processed **{stress_data['resumes_processed']}** resumes in **{stress_data['total_latency_seconds']}s**")
                st.info(f"Average throughput latency: {stress_data['avg_latency_per_resume']}s per resume.")
            else: st.error("Stress test engine disconnected.")


elif nav_mode == "🔮 AI Foresight":
    st.markdown("### 🔮 Strategic AI Foresight & Value Analytics")
    st.markdown("Predict long-term talent success, visualize cultural alignment, and track platform ROI.")
    
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    # 1. Platform ROI Analytics
    st.markdown("#### 💰 Platform ROI & Economic Value")
    r_res = requests.get(f"{API_URL}/analytics/roi", headers=headers)
    if r_res.status_code == 200:
        roi = r_res.json()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Financial Savings", f"${roi['estimated_cost_savings_usd']}", delta="+$5k")
        c2.metric("Time Saved", f"{roi['total_time_saved_hours']} hrs")
        c3.metric("Hire Quality Lift", roi['quality_of_hire_lift'])
        c4.metric("ROI Multiple", roi['roi_multiple'], help="Value generated vs platform cost (mocked)")
        
    st.markdown("---")
    
    # 2. Cultural Alignment & Retention Deep Dive
    f_col1, f_col2 = st.columns([1, 1])
    
    with f_col1:
        st.markdown("#### ⚖️ Cultural Alignment Radar")
        st.info("Visualizing candidate values vs. the 'Company North Star'.")
        # For demo, we use a mock candidate ID
        cul_res = requests.get(f"{API_URL}/analytics/culture-radar/1", headers=headers)
        if cul_res.status_code == 200:
            cdata = cul_res.json()
            fig_cul = go.Figure()
            fig_cul.add_trace(go.Scatterpolar(r=cdata['candidate_vector'], theta=cdata['categories'], fill='toself', name='Candidate'))
            fig_cul.add_trace(go.Scatterpolar(r=cdata['company_vector'], theta=cdata['categories'], fill='toself', name='Company North Star'))
            fig_cul.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 100])), height=350, margin=dict(l=20,r=20,t=20,b=20))
            st.plotly_chart(fig_cul, use_container_width=True, config={'displayModeBar': False})
            st.metric("Cultural Fit Index", f"{cdata['alignment_index']}%")

    with f_col2:
        st.markdown("#### ⏳ AI Retention Forecast")
        st.info("Predictive tenure and flight-risk benchmarking.")
        ret_res = requests.post(f"{API_URL}/analytics/retention/1", headers=headers)
        if ret_res.status_code == 200:
            rdata = ret_res.json()
            st.markdown(f"""
            <div style="background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.3); border-radius: 12px; padding: 20px; text-align: center;">
                <div style="font-size: 14px; color: #a5b4fc;">RETENTION SCORE</div>
                <div style="font-size: 48px; font-weight: 800; color: #fff;">{rdata['retention_score']}</div>
                <div style="font-size: 18px; font-weight: 600; color: {'#10b981' if rdata['risk_level'] == 'Low' else '#f59e0b'};">Risk Level: {rdata['risk_level']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.write(f"**AI Forecast:** {rdata['forecast']}")
            for f in rdata['primary_factors']:
                st.markdown(f"- **{f['factor']}**: {f['impact']}")

    # 3. Proactive Internal Sourcing
    st.markdown("---")
    st.markdown("#### 🎯 Proactive Internal Sourcing (Vault Matches)")
    st.markdown("AI suggests matches from your existing <b>Talent Vault</b> for active roles.", unsafe_allow_html=True)
    if st.button("🔍 Scan Vault for New Role Matches"):
        p_res = requests.get(f"{API_URL}/analytics/proactive-match/1", headers=headers)
        if p_res.status_code == 200:
            matches = p_res.json()
            for m in matches:
                with st.expander(f"✨ {m['name']} - Match: {m['historical_score']}%"):
                    st.write(f"**Vault Tenure:** {m['vault_tenure']}")
                    st.write(f"**Status:** {m['status']}")
                    st.button(f"Re-engage {m['name'].split()[0]}", key=f"re_{m['name']}")
        else: st.error("Vault scan failed.")


elif nav_mode == "🌌 Talent Singularity":
    st.markdown("### 🌌 The Autonomous Talent Singularity")
    st.markdown("Achieve total organizational unity with succession planning, quantum search, and universal connectivity.")
    
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    # 1. AI Succession Architect
    st.markdown("#### 👤 AI Succession Architect")
    st.info("Mapping internal successors and external continuity backups.")
    # For demo, use JD ID 1
    suc_res = requests.get(f"{API_URL}/analytics/succession/1", headers=headers)
    if suc_res.status_code == 200:
        suc = suc_res.json()
        sc1, sc2 = st.columns(2)
        with sc1:
            st.write("**Top Internal Successors:**")
            for s in suc['internal_successors']:
                st.success(f"🔼 {s['name']} ({s['role']}) - Fit: {s['fit_score']}% | Readiness: {s['readiness']}")
        with sc2:
            st.write("**External Market Continuity:**")
            for b in suc['external_backups']:
                st.info(f"🌐 {b['count']} Backups identified in {b['source']} (Avg Match: {b['avg_match']}%)")

    st.markdown("---")
    
    # 2. Quantum Search Core
    st.markdown("#### 🌀 Quantum Search Core (Ultra-High Scale)")
    q_query = st.text_input("Execute Universal Quantum Query", placeholder="e.g. Find me a Staff Principal with Rust Experience and High Retention...")
    if st.button("💫 Execute Quantum Scan"):
        with st.spinner("Analyzing 1,000,000+ profiles across dimensions..."):
            q_res = requests.post(f"{API_URL}/analytics/quantum-search", data={"query": q_query}, headers=headers)
            if q_res.status_code == 200:
                q_data = q_res.json()
                st.success(f"✅ Scan Complete: Found Profile {q_data['top_match_id']} with {q_data['match_confidence']}% confidence.")
                st.write(f"Quantum latency: **{q_data['search_latency_ms']}ms** | Scale: **{q_data['profiles_scanned']}** profiles.")
            else: st.error("Quantum search core offline.")

    st.markdown("---")

    # 3. Autonomous Strategic Architect
    st.markdown("#### 🏗️ Autonomous Strategic Blueprint")
    st.info("AI-driven organizational growth and budgetary recommendations.")
    b_res = requests.get(f"{API_URL}/analytics/strategic-blueprint", headers=headers)
    if b_res.status_code == 200:
        blueprint = b_res.json()
        st.markdown(f"""
        <div style="background: rgba(16,185,129,0.05); border-left: 4px solid #10b981; padding: 20px; border-radius: 8px;">
            <div style="font-weight: 700; color: #10b981; margin-bottom: 5px;">MARKET SENTIMENT</div>
            <div style="color: #fff; margin-bottom: 15px;">{blueprint['market_sentiment']}</div>
            <div style="font-weight: 700; color: #10b981; margin-bottom: 5px;">BUDGETARY GUIDANCE</div>
            <div style="color: #fff; margin-bottom: 15px;">{blueprint['budget_recommendation']}</div>
            <div style="font-weight: 700; color: #10b981; margin-bottom: 5px;">STRATEGIC EVOLUTION TIP</div>
            <div style="color: #fff;">{blueprint['jd_evolution_tip']}</div>
        </div>
        """, unsafe_allow_html=True)

    # 4. Universal HRIS Connectivity
    st.markdown("---")
    st.markdown("#### 🌐 Universal HRIS Connectivity (Nervous System)")
    sync_sys = st.selectbox("Target HRIS / Payroll System", ["Workday", "SAP SuccessFactors", "Greenhouse", "BambooHR"])
    if st.button(f"🔄 Sync Ecosystem with {sync_sys}"):
        with st.spinner(f"Establishing secure tunnel to {sync_sys}..."):
            h_res = requests.post(f"{API_URL}/system/hris-sync", data={"system_name": sync_sys}, headers=headers)
            if h_res.status_code == 200:
                h_data = h_res.json()
                st.success(f"✅ Unified Sync Successful: {h_data['records_synchronized']} records updated.")
                st.write(f"Portal: **{h_data['api_gateway']}**")
            else: st.error("Sync timeout. Verify HRIS credentials.")


elif nav_mode == "🤝 Human-AI Synergy":
    st.markdown("### 🤝 The Universal Human-AI Synergy Hub")
    st.markdown("Unify human intuition with AI cognitive assistance and long-term organizational foresight.")
    
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    # 1. AI Cognitive Nudge Engine
    st.markdown("#### 🧠 AI Cognitive Nudge Engine")
    st.info("Real-time follow-up prompts for interviewers based on competency gaps.")
    cn_res = requests.get(f"{API_URL}/analytics/cognitive-nudges/1", headers=headers)
    if cn_res.status_code == 200:
        nudges = cn_res.json()['suggested_nudges']
        for n in nudges:
            with st.chat_message("assistant", avatar="🧠"):
                st.write(f"**Topic: {n['topic']}**")
                st.write(f"*Nudge:* {n['nudges']}")
    
    st.markdown("---")
    
    # 2. EQ Blueprint Matrix
    st.markdown("#### ⚖️ Emotional Intelligence (EQ) Blueprint")
    st.info("Benchmarking leadership markers and cultural leadership fit.")
    eq_res = requests.get(f"{API_URL}/analytics/eq-blueprint/1", headers=headers)
    if eq_res.status_code == 200:
        eq_data = eq_res.json()
        fig_eq = px.line_polar(r=eq_data['eq_scores'], theta=eq_data['categories'], line_close=True)
        fig_eq.update_traces(fill='toself', line_color='#8b5cf6')
        fig_eq.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=350, margin=dict(l=20,r=20,t=20,b=20))
        st.plotly_chart(fig_eq, use_container_width=True, config={'displayModeBar': False})
        st.markdown(f"**AI EQ Verdict:** {eq_data['verdict']}")

    st.markdown("---")

    # 3. Autonomous Workforce Roadmap
    st.markdown("#### 📅 Autonomous Workforce Roadmap (24 Months)")
    wr_res = requests.get(f"{API_URL}/analytics/workforce-roadmap", headers=headers)
    if wr_res.status_code == 200:
        roadmap = wr_res.json()
        st.write(f"**Forecast Horizon:** {roadmap['horizon']}")
        for gap in roadmap['predicted_gaps']:
            with st.expander(f"🔮 {gap['skill']} - Urgency: {gap['urgency']}"):
                st.write(f"Time to need: **{gap['time_to_need']}**")
                st.progress(80 if gap['urgency'] == 'Critical' else 50)
        st.warning(f"**Strategic Action:** {roadmap['hiring_roadmap']}")

    # 4. Multi-Modal Ingestion Hub
    st.markdown("---")
    st.markdown("#### 🎥 Multi-Modal Ingestion Hub (Unified Profile)")
    m_type = st.radio("Select Non-Text Signal Source", ["Video Interview Snapshot", "Audio Intro", "Behavioral Simulation Log"], horizontal=True)
    if st.button(f"🌀 Ingest {m_type}"):
        with st.spinner(f"Extracting cognitive signals from {m_type}..."):
            i_res = requests.post(f"{API_URL}/system/modal-ingest", data={"content_type": m_type}, headers=headers)
            if i_res.status_code == 200:
                i_data = i_res.json()
                st.success(f"✅ Ingestion Complete: {i_data['composite_lift']}")
                st.write(f"Extracted: {', '.join(i_data['features_extracted'])}")
            else: st.error("Ingestion failed. Check media format.")


elif nav_mode == "⚖️ Global Sovereignty":
    st.markdown("### ⚖️ Universal Talent Sovereignty & Global Fleet Sync")
    st.markdown("Ensure total trust with immutable verification, candidate sovereignty, and global regional orchestration.")
    
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    # 1. Global Fleet Sync Orchestrator
    st.markdown("#### 🌐 Global Strategic Fleet Sync")
    f_res = requests.get(f"{API_URL}/analytics/fleet-sync", headers=headers)
    if f_res.status_code == 200:
        fleet = f_res.json()
        st.success(f"✅ Ecosystem Unified: {fleet['strategy_hash']} active across all regions.")
        cols = st.columns(len(fleet['active_regions']))
        for i, reg in enumerate(fleet['active_regions']):
            cols[i].markdown(f"""
            <div style="background: rgba(16,185,129,0.1); border: 1px solid #10b981; padding: 10px; border-radius: 8px; text-align: center; font-size: 12px;">
                {reg}<br><b>SYNCED</b>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 2. AI Talent Sovereign Assistant
    st.markdown("#### 👤 AI Talent Sovereign Agent")
    st.info("Direct representation of candidate ethics and verified excellence.")
    sav_res = requests.get(f"{API_URL}/analytics/sovereign-agent/1", headers=headers)
    if sav_res.status_code == 200:
        sagent = sav_res.json()
        st.write(f"**Agent Status:** {sagent['agent_status']}")
        with st.expander("Ethics & Boundaries Representation"):
            for key, val in sagent['ethics_representation'].items():
                st.write(f"🔸 **{key.replace('_', ' ').title()}:** {val}")
        
        st.write("**Advocated Competencies (Verified Artifacts):**")
        for adv in sagent['advocated_skills']:
            st.markdown(f"- ✨ **{adv['skill']}**: {adv['proof']}")

    st.markdown("---")

    # 3. Decentralized Verified Skill Vault
    st.markdown("#### 🛡️ Decentralized Verified Vault")
    st.info("Immutable records of trust-verified professional milestones.")
    vv_res = requests.get(f"{API_URL}/analytics/verified-vault/1", headers=headers)
    if vv_res.status_code == 200:
        vv = vv_res.json()
        st.metric("Global Trust Score", f"{vv['trust_score']}/100")
        for mile in vv['verified_milestones']:
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; margin-bottom: 10px;">
                <div style="font-weight: 700;">{mile['milestone']}</div>
                <div style="font-size: 11px; color: #9ca3af;">Issuer: {mile['issuer']} | Date: {mile['verified_on']}</div>
                <div style="font-family: monospace; font-size: 10px; color: #6366f1;">Hash: {mile['hash']}</div>
            </div>
            """, unsafe_allow_html=True)

    # 4. Universal Immutable Audit Trail
    st.markdown("---")
    st.markdown("#### 📑 Universal Immutable Audit Trail")
    if st.button("🔗 Generate Cryptographic Lifecycle Proof"):
        ia_res = requests.get(f"{API_URL}/system/immutable-audit/1", headers=headers)
        if ia_res.status_code == 200:
            trails = ia_res.json()
            for t in trails:
                st.markdown(f"**[{t['timestamp']}]** {t['action']} | `Signed by: {t['signed_by']}`")
                st.caption(f"Signature: {t['signature']}")
        else: st.error("Audit trail serialization failed.")


elif nav_mode == "🌌 Organizational Nexus":
    st.markdown("### 🌌 The Universal Organizational Talent Nexus")
    st.markdown("Autonomous succession, high-fidelity workforce simulation, and immutable lifecycle governance.")
    
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    # 1. AI Succession Regent
    st.markdown("#### 🛡️ AI Succession Regent")
    st.info("The guardian of organizational continuity and autonomous leadership growth.")
    sr_res = requests.get(f"{API_URL}/analytics/succession-regent/1", headers=headers)
    if sr_res.status_code == 200:
        sr = sr_res.json()
        st.write(f"**Succession Strength:** {sr['succession_strength']}")
        st.write(f"**Primary Successor identified:** {sr['primary_successor']}")
        st.markdown("**Bridge Training Roadmap Active:**")
        for bt in sr['bridge_training_roadmap']:
            st.markdown(f"- 🎓 **{bt['skill']}** | Status: `{bt['status']}` | ETA: {bt['eta']}")
        st.success(f"**Regent Verdict:** {sr['regent_action']}")
    
    st.markdown("---")
    
    # 2. Quantum Workforce Simulator (5-Year)
    st.markdown("#### 🔮 Quantum Workforce Simulator")
    qs_res = requests.get(f"{API_URL}/analytics/quantum-simulator", headers=headers)
    if qs_res.status_code == 200:
        qs = qs_res.json()
        st.metric("5-Year Confidence", qs['simulation_confidence'])
        st.write(f"**Velocity Impact:** {qs['velocity_impact']}")
        st.write(f"**Financial ROI Forecast:** {qs['financial_roi']}")
        with st.expander("Strategic Risk Pockets"):
            for risk in qs['risk_pockets']:
                st.warning(f"⚠️ {risk}")

    st.markdown("---")

    # 3. Universal Hire-to-Retire Immutable Ledger
    st.markdown("#### 📜 Eternal Lifecycle Ledger")
    st.info("The permanent professional narrative of every talent milestone.")
    el_res = requests.get(f"{API_URL}/system/eternal-ledger/1", headers=headers)
    if el_res.status_code == 200:
        el = el_res.json()
        for ev in el['events']:
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.03); border-left: 3px solid #6366f1; padding: 12px; margin-bottom: 8px;">
                <div style="font-size: 13px; font-weight: 600;">{ev['event']}</div>
                <div style="font-size: 11px; color: #9ca3af;">Node: {ev['node']} | Date: {ev['date']}</div>
                <div style="font-size: 10px; color: #4338ca; font-family: monospace;">Hash: {ev['hash']}</div>
            </div>
            """, unsafe_allow_html=True)

    # 4. Autonomous Strategic Governance Dashboard
    st.markdown("---")
    st.markdown("#### ⚖️ Autonomous Nexus Governance")
    ng_res = requests.get(f"{API_URL}/system/nexus-governance", headers=headers)
    if ng_res.status_code == 200:
        ng = ng_res.json()
        st.write(f"**Ethical Audit Status:** {ng['ethical_audit']}")
        st.write(f"**Mission Alignment Score:** {ng['mission_alignment']}")
        st.progress(97)
        st.caption(f"Last Governance Heartbeat: {ng['last_audit_timestamp']}")
    else: st.error("Governance node unavailable.")


elif nav_mode == "🌌 The Singularity":
    st.markdown("### 🌌 The Universal Talent Singularity (Final State)")
    st.markdown("Autonomous ecosystem evolution, multi-verse strategy simulation, and perpetual ethical alignment.")
    
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    # 1. AI Evolutionary Architect
    st.markdown("#### 🧬 AI Evolutionary Architect (The Origin)")
    ea_res = requests.get(f"{API_URL}/analytics/evolution-architect", headers=headers)
    if ea_res.status_code == 200:
        ea = ea_res.json()
        st.success(f"✅ System Mode: {ea['architect_mode']} | Velocity: {ea['evolution_velocity']}")
        for upg in ea['proposed_upgrades']:
            st.markdown(f"**Upgrade:** {upg['upgrade']} → *Impact: {upg['impact']}*")
        st.caption(f"Total Autonomous Patches Applied: {ea['applied_patches']}")
    
    st.markdown("---")
    
    # 2. Quantum Multi-Verse Strategy Engine
    st.markdown("#### 🔮 Quantum Multi-Verse Strategy")
    st.info("The single most optimal path to organizational dominance selected from 1,024 parallel futures.")
    mv_res = requests.get(f"{API_URL}/analytics/multiverse-strategy", headers=headers)
    if mv_res.status_code == 200:
        mv = mv_res.json()
        st.metric("Strategy Confidence", mv['strategy_confidence'])
        for step in mv['path_to_dominance']:
            st.markdown(f"**[Year {step['year']}]** {step['action']} | *{step['impact']}*")
    
    st.markdown("---")

    # 3. Universal Cross-Institutional Sector Bridge
    st.markdown("#### 🌐 Cross-Institutional Talent Bridge")
    sb_res = requests.get(f"{API_URL}/analytics/sector-bridge", headers=headers)
    if sb_res.status_code == 200:
        sb = sb_res.json()
        st.write(f"Global Intelligence Pooling: **{sb['global_intelligence_pooling']}**")
        for bridge in sb['active_sector_bridges']:
            st.markdown(f"✨ **{bridge['sector']}** | Partners: {bridge['partners']} | Synergy: `{bridge['synergy_index']}`")

    # 4. Autonomous Final State Governance
    st.markdown("---")
    st.markdown("#### ⚖️ Autonomous Singularity Governance")
    sg_res = requests.get(f"{API_URL}/system/singularity-governance", headers=headers)
    if sg_res.status_code == 200:
        sg = sg_res.json()
        st.write(f"**Universal Ethical Alignment:** {sg['universal_ethics_alignment']}")
        st.write(f"**Destiny Status:** {sg['organizational_destiny_status']}")
        st.success(f"**Singularity Status:** {sg['governance_singularity']}")
    else: st.error("Singularity node offline.")


