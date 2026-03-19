"""
ResumeAI Pro - Neural Recruitment Intelligence Platform
Version 5.0 - Ultra Modern UI
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils import (
    extract_text_from_pdf,
    calculate_similarity,
    find_missing_skills,
    extract_semantic_skills,
    calculate_skill_depth,
    detect_bias_indicators,
    detect_experience_years,
    calculate_ats_score,
    calculate_detailed_match,
)
import time
from datetime import datetime

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
    page_title="ResumeAI Pro",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "demo_loaded" not in st.session_state:
    st.session_state.demo_loaded = False

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif !important; }
.stApp { background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%); }
#MainMenu, footer, header { visibility: hidden; }
.glass-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 20px; padding: 24px; }
.main-header { background: linear-gradient(135deg, rgba(102,126,234,0.2), rgba(118,75,162,0.2)); border: 1px solid rgba(102,126,234,0.3); border-radius: 24px; padding: 40px; text-align: center; margin-bottom: 30px; }
.main-header h1 { font-size: 42px; font-weight: 900; background: linear-gradient(135deg, #667eea, #764ba2, #f093fb); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; }
.kpi-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 20px; padding: 24px; text-align: center; position: relative; }
.kpi-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, #667eea, #764ba2); border-radius: 20px 20px 0 0; }
.kpi-label { font-size: 11px; text-transform: uppercase; letter-spacing: 2px; color: rgba(255,255,255,0.4); margin-bottom: 8px; }
.kpi-value { font-size: 38px; font-weight: 800; color: #fff; }
.kpi-value.green { color: #10b981; }
.kpi-value.gradient { background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.badge { display: inline-block; padding: 6px 16px; border-radius: 50px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
.badge-success { background: rgba(16,185,129,0.2); color: #10b981; }
.badge-danger { background: rgba(239,68,68,0.2); color: #ef4444; }
.podium-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 24px; padding: 30px; text-align: center; }
.stButton > button { background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; border-radius: 14px; padding: 16px 32px; font-size: 16px; font-weight: 600; }
.stTabs [data-baseweb="tab-list"] { background: rgba(255,255,255,0.03); border-radius: 16px; padding: 6px; }
.stTabs [data-baseweb="tab"] { border-radius: 12px; padding: 14px 28px; font-weight: 600; color: rgba(255,255,255,0.5); }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #667eea, #764ba2) !important; color: white !important; }
[data-testid="stSidebar"] { background: rgba(15,15,35,0.95) !important; }
</style>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown(
        """<div style="text-align: center; padding: 20px 0;"><div style="font-size: 48px;">🤖</div><h1 style="font-size: 22px; font-weight: 800; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 10px 0 0 0;">ResumeAI Pro</h1></div>""",
        unsafe_allow_html=True,
    )
    st.markdown("---")
    if st.button("🚀 Load Sample Data", use_container_width=True):
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
    st.markdown("**📄 Upload Resumes**")
    uploaded_files = st.file_uploader(
        "PDF or TXT", type=["pdf", "txt"], accept_multiple_files=True
    )
    st.markdown("---")
    threshold = st.slider("Match Threshold", 0, 100, 50)
    enable_bias = st.checkbox("Bias Detection", value=True)

st.markdown(
    """<div class="main-header"><h1>Smart Resume Matcher</h1><p style="color: rgba(255,255,255,0.6); margin-top: 10px;">AI-Powered Resume Screening & Candidate Ranking</p></div>""",
    unsafe_allow_html=True,
)

st.markdown("**📋 Job Description**")
jd_text = SAMPLE_JD if st.session_state.get("demo_loaded") else ""
job_description = st.text_area(
    "Paste job description here...", jd_text, height=150, label_visibility="collapsed"
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_clicked = st.button(
        "🔍 Analyze Candidates", type="primary", use_container_width=True
    )

if analyze_clicked:
    if st.session_state.get("demo_loaded") and st.session_state.get("demo_jd"):
        job_desc = st.session_state.demo_jd
        resumes = st.session_state.demo_resumes
    elif job_description and uploaded_files:
        job_desc = job_description
        resumes = [(f.name, None) for f in uploaded_files]
    else:
        st.error("⚠️ Load demo or enter JD + upload resumes")
        st.stop()

    with st.spinner("Analyzing..."):
        progress = st.progress(0)
        results = []
        files = resumes if resumes else uploaded_files

        for idx, item in enumerate(files):
            if st.session_state.get("demo_loaded"):
                name, text = item
            else:
                f = item
                name = f.name
                text = (
                    f.read().decode("utf-8")
                    if name.endswith(".txt")
                    else extract_text_from_pdf(f)
                )

            if text and len(text) > 50:
                detailed = calculate_detailed_match(job_desc, text)
                ats = calculate_ats_score(text)
                exp = detect_experience_years(text)
                req_skills = extract_semantic_skills(job_desc)
                cand_skills = detailed["all_resume_skills"]
                missing = list(set(req_skills) - set([s.lower() for s in cand_skills]))

                results.append(
                    {
                        "Rank": 0,
                        "Candidate": name.replace(".pdf", "").replace(".txt", ""),
                        "Score": round(detailed["total"], 1),
                        "Skill_Score": detailed["skill_score"],
                        "Exp_Score": detailed["experience_score"],
                        "KW_Score": detailed["keyword_score"],
                        "ATS": ats,
                        "Experience": exp,
                        "Skills_Count": len(cand_skills),
                        "Missing": missing[:5],
                        "Missing_Count": len(missing),
                        "Status": "Shortlisted"
                        if detailed["total"] >= threshold
                        else "Not Selected",
                        "Top_Skills": cand_skills[:6],
                    }
                )
            progress.progress((idx + 1) / len(files))
            time.sleep(0.3)

    if results:
        results = sorted(results, key=lambda x: x["Score"], reverse=True)
        for i, r in enumerate(results):
            r["Rank"] = i + 1
        df = pd.DataFrame(results)

        st.markdown("### 📊 Results")
        kpi_cols = st.columns(5)
        metrics = [
            ("Total", len(df), "gradient"),
            ("Shortlisted", len(df[df["Status"] == "Shortlisted"]), "green"),
            (f"{df['Score'].mean():.0f}%", "Avg", "gradient"),
            (f"{df['ATS'].mean():.0f}%", "ATS", "gradient"),
            (f"{df['Experience'].mean():.1f}yr", "Exp", "gradient"),
        ]
        for col, (val, label, color) in zip(kpi_cols, metrics):
            with col:
                st.markdown(
                    f"""<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value {color}">{val}</div></div>""",
                    unsafe_allow_html=True,
                )

        tab1, tab2, tab3, tab4 = st.tabs(
            ["🏆 Rankings", "📈 Analytics", "🔬 Details", "💾 Export"]
        )

        with tab1:
            if len(df) >= 3:
                podium_cols = st.columns(3)
                for col, idx, emoji, color in zip(
                    podium_cols,
                    [0, 1, 2],
                    ["🥇", "🥈", "🥉"],
                    ["#fbbf24", "#94a3b8", "#b45309"],
                ):
                    with col:
                        c = df.iloc[idx]
                        st.markdown(
                            f"""<div class="podium-card"><div style="font-size: 48px;">{emoji}</div><div style="font-size: 18px; font-weight: 700; color: #fff; margin: 10px 0;">{c["Candidate"]}</div><div style="font-size: 32px; font-weight: 800; color: {color};">{c["Score"]}%</div><span class="badge {"badge-success" if c["Status"] == "Shortlisted" else "badge-danger"}">{c["Status"]}</span><br><br><div style="font-size: 12px; color: rgba(255,255,255,0.4);">📧 {c["Skills_Count"]} skills | ⏱️ {c["Experience"]} yrs</div></div>""",
                            unsafe_allow_html=True,
                        )
            st.markdown("---")
            st.dataframe(
                df[["Rank", "Candidate", "Score", "Experience", "ATS", "Status"]],
                use_container_width=True,
            )

        with tab2:
            fig_bar = go.Figure()
            colors = [
                "#10b981" if s == "Shortlisted" else "#ef4444" for s in df["Status"]
            ]
            fig_bar.add_trace(
                go.Bar(
                    x=df["Candidate"],
                    y=df["Score"],
                    marker_color=colors,
                    text=df["Score"],
                )
            )
            fig_bar.update_layout(
                title="Match Scores",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#fff",
                yaxis=dict(range=[0, 100]),
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with tab3:
            for _, row in df.iterrows():
                with st.expander(
                    f"#{row['Rank']} {row['Candidate']} - {row['Score']}%"
                ):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Match Score", f"{row['Score']}%")
                        st.metric("Experience", f"{row['Experience']} years")
                    with col2:
                        st.metric("ATS Score", f"{row['ATS']}%")
                        st.metric("Skills Found", row["Skills_Count"])
                    with col3:
                        st.metric("Missing Skills", row["Missing_Count"])
                    if row["Top_Skills"]:
                        st.markdown(
                            "**🎯 Skills:** "
                            + ", ".join([f"`{s}`" for s in row["Top_Skills"]])
                        )
                    if row["Missing"]:
                        st.markdown(
                            "**⚠️ Missing:** "
                            + ", ".join([f"`{s}`" for s in row["Missing"]])
                        )

        with tab4:
            csv = df.to_csv(index=False).encode("utf-8")
            json_data = df.to_json(orient="records")
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "📥 Download CSV",
                    csv,
                    "resume_analysis.csv",
                    "text/csv",
                    use_container_width=True,
                )
            with col2:
                st.download_button(
                    "📄 Download JSON",
                    json_data,
                    "resume_analysis.json",
                    "application/json",
                    use_container_width=True,
                )
    else:
        st.error("No valid resumes found")

st.markdown(
    """<br><br><div style="text-align: center; color: rgba(255,255,255,0.3); font-size: 12px;">ResumeAI Pro v5.0 | Mini Project</div>""",
    unsafe_allow_html=True,
)
