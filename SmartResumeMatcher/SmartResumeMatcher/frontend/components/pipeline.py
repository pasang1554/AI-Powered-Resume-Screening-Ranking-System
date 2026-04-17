import streamlit as st
import requests
import time

@st.fragment
def render_talent_pipeline(df, auth_header, API_URL):
    st.markdown(
        """<div style="background: rgba(99, 102, 241, 0.05); border-left: 4px solid #6366F1; padding: 1rem; border-radius: 8px; margin-bottom: 2rem;">
            <p style="margin: 0; color: #A5B4FC; font-weight: 600;">Neural Logistic Orchestration</p>
            <p style="margin: 0; font-size: 0.85rem; color: #64748B;">Monitor candidate velocity through the institutional recruitment lifecycle.</p>
        </div>""", 
        unsafe_allow_html=True
    )
    
    stages = ["Shortlisted", "Interviewing", "Offer Extended", "Hired", "Not Selected"]
    cols = st.columns(len(stages))
    
    for i, stage in enumerate(stages):
        with cols[i]:
            st.markdown(
                f"""<div style="background: rgba(255,255,255,0.03); padding: 0.75rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 1rem; text-align: center;">
                    <span style="font-size: 0.75rem; font-weight: 800; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em;">{stage}</span>
                </div>""",
                unsafe_allow_html=True
            )
            
            # Filter candidates for this stage
            stage_candidates = df[df["Status"] == stage]
            
            if stage_candidates.empty:
                st.markdown('<p style="color: #475569; font-size: 0.8rem; text-align: center; font-style: italic; padding: 1rem;">Vacuum detected</p>', unsafe_allow_html=True)
            else:
                for _, sc in stage_candidates.iterrows():
                    with st.container(border=True):
                        st.markdown(f"**{sc['Candidate']}**")
                        st.markdown(f"Match: `{sc['Score']}%` | ATS: `{sc.get('ATS', 0)}%`")
                        
                        new_status = st.selectbox("Transition", stages, index=stages.index(stage), key=f"pipe_status_{sc['id']}", label_visibility="collapsed")
                        if new_status != stage:
                            if st.button("Move ⚡", key=f"pipe_btn_{sc['id']}", width='stretch'):
                                p_res = requests.patch(f"{API_URL}/analytics/status/{sc.get('id')}", json={"status": new_status}, headers=auth_header)
                                if p_res.status_code == 200:
                                    if st.session_state.results:
                                        for res_item in st.session_state.results:
                                            if res_item.get("id") == sc.get("id"):
                                                res_item["Status"] = new_status
                                    st.success("Synchronized")
                                    time.sleep(0.5)
                                    st.rerun(scope="fragment")
                                else: st.error("Sync Error")
