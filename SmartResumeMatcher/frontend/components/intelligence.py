import streamlit as st
import pandas as pd
import requests
import json

def render_intelligence_suite(candidate, jd_content, groq_api_key, api_url, auth_header):
    """
    Renders the advanced AI intelligence tools for a specific candidate.
    """
    if not groq_api_key:
        st.warning("⚠️ Groq API Key is missing. Please provide it in the sidebar to enable these features.")
        return

    col_avatar, col_title = st.columns([1, 8])
    with col_avatar:
        try:
            st.image("frontend/assets/candidate_icon.png", width=60)
        except:
            st.markdown("👤")
    with col_title:
        st.markdown(f"### 🧠 Intelligence Suite: {candidate['Candidate']}")
    
    # Download Report Button
    try:
        if candidate.get("id") and candidate.get("AI_Evaluation"):
            exp_res = requests.get(f"{api_url}/analyze/export/{candidate['id']}", headers=auth_header)
            if exp_res.status_code == 200:
                st.download_button(
                    label="📥 Download Intelligence Report (PDF)",
                    data=exp_res.content,
                    file_name=f"intelligence_report_{candidate['Candidate'].replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
    except:
        pass

    # Tabs for different intelligence modules
    tab_eval, tab_coach, tab_scorecard, tab_simulator = st.tabs([
        "📋 AI Evaluation", 
        "🛠️ ATS Coaching", 
        "📝 Interview Scorecard", 
        "🎭 Roleplay Simulator"
    ])

    with tab_eval:
        ai_eval = candidate.get("AI_Evaluation")
        if ai_eval and isinstance(ai_eval, dict):
            if "error" in ai_eval:
                st.error(f"Neural Core Error: {ai_eval['error']}")
                st.info("This often happens due to API rate limits. Try running the analysis again in a few moments.")
            else:
                render_deep_evaluation(ai_eval)
        else:
            st.info("No deep evaluation data available for this candidate. Run a new analysis with a Groq key.")

    with tab_coach:
        if st.button("Generate Coaching Report ⚡", key=f"coach_btn_{candidate['id']}"):
            with st.spinner("Generating professional coaching..."):
                payload = {
                    "job_description": jd_content,
                    "resume_text": candidate.get("resume_text", ""),
                    "groq_api_key": groq_api_key
                }
                res = requests.post(f"{api_url}/analyze/coach", data=payload, headers=auth_header)
                if res.status_code == 200:
                    st.session_state[f"coach_{candidate['id']}"] = res.json()
                else:
                    st.error(f"Failed to generate coaching: {res.text}")
        
        if f"coach_{candidate['id']}" in st.session_state:
            render_ats_coaching(st.session_state[f"coach_{candidate['id']}"])

    with tab_scorecard:
        if st.button("Create Interview Scorecard 📝", key=f"score_btn_{candidate['id']}"):
            with st.spinner("Designing structured scorecard..."):
                payload = {
                    "job_description": jd_content,
                    "groq_api_key": groq_api_key
                }
                res = requests.post(f"{api_url}/analyze/scorecard", data=payload, headers=auth_header)
                if res.status_code == 200:
                    st.session_state[f"scorecard_{candidate['id']}"] = res.json()
                else:
                    st.error(f"Failed to generate scorecard: {res.text}")

        if f"scorecard_{candidate['id']}" in st.session_state:
            render_interview_scorecard(st.session_state[f"scorecard_{candidate['id']}"])

    with tab_simulator:
        if st.button("Run Roleplay Simulation 🎭", key=f"sim_btn_{candidate['id']}"):
            with st.spinner("Simulating candidate psyche..."):
                payload = {
                    "candidate_id": candidate['candidate_id'],
                    "groq_api_key": groq_api_key
                }
                res = requests.post(f"{api_url}/analyze/simulate", data=payload, headers=auth_header)
                if res.status_code == 200:
                    st.session_state[f"sim_{candidate['id']}"] = res.json()
                else:
                    st.error(f"Failed to run simulation: {res.text}")

        if f"sim_{candidate['id']}" in st.session_state:
            render_roleplay_simulator(st.session_state[f"sim_{candidate['id']}"])

def render_deep_evaluation(data):
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.markdown(f"#### Executive Summary")
    st.write(data.get("summary", "No summary available."))
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**💎 Key Strengths**")
        for s in data.get("strengths", []):
            st.markdown(f"- {s}")
    with col2:
        st.markdown("**⚠️ Potential Gaps**")
        for w in data.get("weaknesses", []):
            st.markdown(f"- {w}")
    
    st.markdown(f"**Verdict:** `{data.get('recommendation', 'N/A')}`")
    st.markdown('</div>', unsafe_allow_html=True)

def render_ats_coaching(data):
    if "error" in data:
        st.error(data["error"])
        return

    st.success(data.get("overall_feedback", "Coaching complete."))
    
    st.markdown("#### 🛠️ Critical Resume Fixes")
    for fix in data.get("critical_fixes", []):
        st.info(fix)
        
    st.markdown("#### 🚀 Impact Statement Upgrades")
    for stmt in data.get("impact_statements", []):
        st.code(stmt)

def render_interview_scorecard(data):
    if "error" in data:
        st.error(data["error"])
        return

    st.markdown("#### Structured Evaluation Criteria")
    criteria = data.get("evaluation_criteria", [])
    if criteria:
        df_criteria = pd.DataFrame(criteria)
        st.table(df_criteria[["category", "weight", "key_questions"]])
    
    with st.expander("Behavioral Questions"):
        for q in data.get("behavioral_questions", []):
            st.markdown(f"- {q}")

def render_roleplay_simulator(data):
    st.markdown("#### Autonomous Personality Prediction")
    st.markdown(data.get("simulation", "No simulation result."))
