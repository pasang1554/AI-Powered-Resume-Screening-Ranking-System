import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

def render_interview_manager(api_url, auth_header):
    st.markdown(
        """<div style="background: linear-gradient(90deg, #10B981, #059669); padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;">
            <h2 style="margin: 0; color: white; display: flex; align-items: center; gap: 0.5rem;">
                🤝 Strategic Interview Orchestration
            </h2>
            <p style="margin: 0; color: rgba(255,255,255,0.8); font-size: 0.9rem;">Manage the institutional candidate lifecycle and record deep intelligence feedback.</p>
        </div>""", 
        unsafe_allow_html=True
    )

    tab_monitor, tab_schedule = st.tabs(["📅 Upcoming Sessions", "➕ Schedule New Session"])

    with tab_monitor:
        interviews = []
        try:
            res = requests.get(f"{api_url}/interviews", headers=auth_header)
            if res.status_code == 200:
                interviews = res.json()
            else: st.error("Failed to load interviews.")
        except Exception as e: st.error(f"Connection error: {e}")

        if not interviews:
            st.info("No interviews currently scheduled. Transition a candidate to 'Interviewing' and schedule a session.")
        else:
            for iv in interviews:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.markdown(f"**Candidate ID: {iv['candidate_id']}**")
                        st.caption(f"📅 {iv['interview_date'].replace('T', ' ')}")
                        st.markdown(f"📍 Medium: `{iv['medium']}` | Status: `{iv['status']}`")
                    
                    with col2:
                        # ICS Export
                        try:
                            ics_res = requests.get(f"{api_url}/interviews/{iv['id']}/ics", headers=auth_header)
                            if ics_res.status_code == 200:
                                st.download_button(
                                    "📅 Export to Calendar",
                                    ics_res.content,
                                    file_name=f"interview_{iv['id']}.ics",
                                    mime="text/calendar",
                                    key=f"ics_{iv['id']}"
                                )
                        except: pass

                    with col3:
                        if st.button("📝 Record Feedback", key=f"fb_btn_{iv['id']}"):
                            st.session_state[f"recording_fb_{iv['id']}"] = True
                    
                    if st.session_state.get(f"recording_fb_{iv['id']}"):
                        with st.form(key=f"fb_form_{iv['id']}"):
                            st.markdown("#### Post-Interview Intelligence")
                            score = st.slider("Interviewer Score", 0.0, 10.0, 5.0)
                            summary = st.text_area("Feedback Summary", placeholder="Key takeaways from the session...")
                            new_status = st.selectbox("Update Candidate Status", ["Scheduled", "Completed", "Cancelled", "Hired", "Rejected"])
                            
                            if st.form_submit_button("Submit Evaluation"):
                                fb_data = {
                                    "interviewer_score": score,
                                    "feedback_summary": summary,
                                    "status": new_status
                                }
                                # Using standard form data as per backend/routes/interviews.py
                                try:
                                    # Note: backend uses standard Form() for optional fields
                                    up_res = requests.patch(
                                        f"{api_url}/interviews/{iv['id']}/feedback", 
                                        data=fb_data, 
                                        headers=auth_header
                                    )
                                    if up_res.status_code == 200:
                                        st.success("Feedback Recorded")
                                        st.session_state[f"recording_fb_{iv['id']}"] = False
                                        st.rerun()
                                    else: st.error(f"Failed to record: {up_res.text}")
                                except Exception as e: st.error(str(e))

    with tab_schedule:
        st.markdown("#### Initialize New Interaction")
        
        # Need to list candidates to select from
        candidates = []
        try:
            cand_res = requests.get(f"{api_url}/candidates/vault", headers=auth_header)
            if cand_res.status_code == 200:
                candidates = cand_res.json()
        except: pass

        if not candidates:
            st.warning("No candidates found in the system. Run an analysis first.")
        else:
            with st.form("schedule_form"):
                cand_names = {c['id']: c['name'] for c in candidates}
                selected_cand_id = st.selectbox("Select Candidate", options=list(cand_names.keys()), format_func=lambda x: cand_names[x])
                
                col_d, col_t = st.columns(2)
                with col_d:
                    iv_date = st.date_input("Interview Date", datetime.now() + timedelta(days=1))
                with col_t:
                    iv_time = st.time_input("Start Time", value=datetime.now().time())
                
                medium = st.selectbox("Medium", ["Zoom", "Google Meet", "Microsoft Teams", "Phone Call", "On-site"])
                notes = st.text_area("Initial Notes / Instructions")

                if st.form_submit_button("🚀 Finalize Schedule"):
                    combined_dt = datetime.combine(iv_date, iv_time)
                    payload = {
                        "candidate_id": selected_cand_id,
                        "interview_date": combined_dt.isoformat(),
                        "medium": medium,
                        "notes": notes,
                        "status": "Scheduled"
                    }
                    try:
                        sv_res = requests.post(f"{api_url}/interviews", json=payload, headers=auth_header)
                        if sv_res.status_code == 200:
                            st.success(f"Interview scheduled for {combined_dt.strftime('%b %d, %H:%M')}")
                            time.sleep(1)
                            st.rerun()
                        else: st.error(f"Scheduling failed: {sv_res.text}")
                    except Exception as e: st.error(str(e))
