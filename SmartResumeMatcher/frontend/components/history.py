import streamlit as st
import pandas as pd
import requests
import time

def load_project_to_dashboard(jd_id, API_URL, auth_header):
    try:
        jd_res = requests.get(f"{API_URL}/job-descriptions", headers=auth_header)
        if jd_res.status_code == 200:
            jds = jd_res.json()
            target_jd = next((j for j in jds if j['id'] == jd_id), None)
            if target_jd:
                st.session_state.job_desc_input = target_jd.get('content', target_jd.get('text', ''))
        
        cand_res = requests.get(f"{API_URL}/job-descriptions/{jd_id}/analyses", headers=auth_header)
        if cand_res.status_code == 200:
            raw_results = cand_res.json()
            ui_results = []
            for r in raw_results:
                ui_results.append({
                    "id": r.get("id"),
                    "candidate_id": r.get("candidate_id"),
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
                    "resume_text": r.get("resume_text", ""),
                    "created_at": r.get("created_at")
                })
            st.session_state.results = ui_results
            st.session_state.last_jd_id = jd_id
            st.success(f"✅ Project {jd_id} restored successfully!")
            time.sleep(1)
            st.rerun()
    except Exception as e:
        st.error(f"Restoration failed: {e}")

def render_history_view(API_URL, auth_header, groq_api_key):
    st.markdown("### 🗄️ Recruitment Intelligence Pool")
    st.markdown("Advanced filtering and historical intelligence retrieved directly from the secure candidate vault.")
    
    filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])
    with filter_col1:
        search_name = st.text_input("🔍 Search Candidate Name", placeholder="Enter name to filter...", key="hist_search")
    with filter_col2:
        status_filter = st.selectbox("Status", ["All", "Shortlisted", "Not Selected"], key="hist_status")
    with filter_col3:
        verdict_filter = st.selectbox("AI Verdict", ["All", "Ready to Hire", "Not Ready"], key="hist_verdict")
        
    try:
        params = {}
        if status_filter != "All":
            params["status"] = status_filter
        
        res = requests.get(f"{API_URL}/analytics/list", headers=auth_header, params=params)
        if res.status_code == 200:
            history_data = res.json()
            if history_data:
                if search_name:
                    history_data = [a for a in history_data if search_name.lower() in a["candidate_name"].lower()]
                
                if verdict_filter != "All":
                    history_data = [a for a in history_data if a.get("ai_evaluation", {}).get("hiring_status") == verdict_filter]

                if history_data:
                    df_hist = pd.DataFrame(history_data)
                    st.markdown("---")
                    st.markdown("#### ⚡ Strategic Health Index")
                    h_col1, h_col2, h_col3 = st.columns(3)
                    with h_col1:
                        avg_vel = round(df_hist['match_score'].count() / 7, 1) if not df_hist.empty else 0
                        st.metric("Pipeline Velocity", f"{avg_vel} cand/wk", delta="12%")
                    with h_col2:
                        avg_q = round(df_hist['match_score'].mean(), 1) if not df_hist.empty else 0
                        st.metric("Quality of Hire Index", f"{avg_q}%", delta="5%")
                    with h_col3:
                        conv_rate = round((len(df_hist[df_hist['status'] == 'Shortlisted']) / len(df_hist) * 100), 1) if not df_hist.empty else 0
                        st.metric("Strategic Yield", f"{conv_rate}%")
                    
                    hist_tab1, hist_tab2, hist_tab3 = st.tabs(["📁 Project Vault", "📜 Compliance Audit Logs", "💎 Global Talent Vault"])
                    
                    with hist_tab1:
                        st.markdown("#### Managed Recruitment Projects")
                        unique_jds = df_hist.groupby('job_description_id').agg({
                            'created_at': 'max',
                            'candidate_name': 'count'
                        }).sort_values('created_at', ascending=False)
                        
                        for jd_id, info in unique_jds.iterrows():
                            with st.container(border=True):
                                p_col1, p_col2, p_col3, p_col4 = st.columns([2, 1, 1, 1])
                                with p_col1:
                                    st.markdown(f"**Project Cluster {jd_id}**")
                                    st.caption(f"Last Interaction: {str(info['created_at'])[:16]}")
                                with p_col2:
                                    st.markdown(f"👥 `{info['candidate_name']}` Candidates")
                                with p_col3:
                                    if st.button(f"🔌 Restore", key=f"restore_{jd_id}", width='stretch'):
                                        load_project_to_dashboard(jd_id, API_URL, auth_header)
                                with p_col4:
                                    # Added New Modular Controls
                                    if st.button(f"📥 Export", key=f"export_{jd_id}", width='stretch'):
                                        e_res = requests.get(f"{API_URL}/job-descriptions/{jd_id}/export", headers=auth_header)
                                        if e_res.status_code == 200:
                                            st.download_button("Download CSV", e_res.content, file_name=f"project_{jd_id}.csv", mime="text/csv")
                                        else: st.error("Export Failed")
                                
                                # Candidate Detail Rows for this project
                                project_cands = [a for a in history_data if a['job_description_id'] == jd_id]
                                with st.expander("Show Candidates in this cluster"):
                                    for pc in project_cands:
                                        c_col1, c_col2, c_col3 = st.columns([2, 1, 1])
                                        with c_col1:
                                            st.markdown(f"**{pc['candidate_name']}** (`{pc['match_score']}%`)")
                                        with c_col2:
                                            if st.button("Deep AI 🧠", key=f"hist_intel_{pc['id']}", width='stretch'):
                                                # Use the session state navigation pattern
                                                st.session_state.focus_candidate_name = pc['candidate_name']
                                                st.session_state.nav_selection = "🔍 New Analysis"
                                                # Need to restore results first
                                                load_project_to_dashboard(jd_id, API_URL, auth_header)
                                        with c_col3:
                                            if st.button("Schedule 🤝", key=f"hist_iv_{pc['id']}", width='stretch'):
                                                st.session_state.nav_selection = "🤝 Interview Manager"
                                                st.rerun()
                    
                    with hist_tab2:
                        st.markdown("#### System-Wide Compliance Audit")
                        audit_res = requests.get(f"{API_URL}/audit/logs", headers=auth_header)
                        if audit_res.status_code == 200:
                            audits = audit_res.json()
                            if audits:
                                df_audit = pd.DataFrame(audits)
                                st.dataframe(df_audit[['created_at', 'module', 'action', 'details']], width='stretch', hide_index=True)
                        else: st.error("Failed to load audit logs.")

                    with hist_tab3:
                        st.markdown("#### Strategic Talent Pool")
                        vault_res = requests.get(f"{API_URL}/candidates/vault", headers=auth_header)
                        if vault_res.status_code == 200:
                            vault_cands = vault_res.json()
                            if vault_cands:
                                vdf = pd.DataFrame(vault_cands)
                                st.dataframe(vdf[["name", "email", "skills", "created_at"]], width='stretch', hide_index=True)
                else: st.info("No candidates match your current search filters.")
            else: st.info("No past analyses found in the database. Run a new analysis first.")
            
            st.markdown("---")
            if st.button("🗑️ Wipe Entire Database History", type="primary", width='stretch'):
                try:
                    del_res = requests.post(f"{API_URL}/audit/reset", headers=auth_header)
                    if del_res.status_code == 200:
                        st.success("✅ Database Wiped")
                        time.sleep(1)
                        st.rerun()
                except Exception as e: st.error(f"Connection Error: {e}")
        else: st.error(f"Failed to load history: {res.text}")
    except Exception as e: st.error(f"Error connecting to backend: {e}")
