import streamlit as st
import requests
import io

def render_public_career_portal(api_url):
    """
    Renders the public-facing career portal for external candidates.
    """
    # UI: Back to Selection
    if st.button("⬅️ Back to Portal Selection", key="exit_public_top", type="secondary"):
        st.session_state.entry_mode = None
        st.rerun()

    st.markdown(
        """<div class="candidate-hero">
            <h1>Launch Your Next<br>Institutional Career</h1>
            <p style="font-size: 1.2rem; opacity: 0.9;">Directly connected to the enterprise recruitment nervous system.</p>
        </div>""",
        unsafe_allow_html=True
    )

    try:
        res = requests.get(f"{api_url}/public/jobs")
        if res.status_code == 200:
            jobs = res.json()
        else:
            st.error("Failed to retrieve opportunity clusters.")
            return
    except Exception as e:
        st.error(f"Ecosystem connection error: {e}")
        return

    if not jobs:
        st.info("No active institutional opportunities at this time. Check back during the next singularity event.")
        return

    st.markdown("### 🏢 Available Clusters")
    
    # Simple search bar for public portal
    search_q = st.text_input("🔍 Search Opportunities", placeholder="e.g. Software, Manager...", label_visibility="collapsed")
    
    cols = st.columns(2)
    for idx, job in enumerate(jobs):
        # Filtering logic
        if search_q and search_q.lower() not in job['title'].lower() and search_q.lower() not in job['content'].lower():
            continue
            
        with cols[idx % 2]:
            st.markdown(f'<div class="job-card">', unsafe_allow_html=True)
            st.markdown(f"#### {job['title']}")
            # Show first 150 chars of content
            preview = job['content'][:150] + "..." if len(job['content']) > 150 else job['content']
            st.write(preview)
            
            if st.button(f"View & Apply 🚀", key=f"apply_btn_{job['id']}", width='stretch'):
                st.session_state.applying_for_id = job['id']
                st.session_state.applying_for_title = job['title']
            
            if st.session_state.get("applying_for_id") == job['id']:
                with st.form(key=f"apply_form_{job['id']}"):
                    st.markdown(f"**Application Gateway: {job['title']}**")
                    name = st.text_input("Full Name", placeholder="John Doe")
                    email = st.text_input("Institutional Email", placeholder="john@example.com")
                    resume_file = st.file_uploader("Upload Neural Artifact (PDF/TXT Resume)", type=["pdf", "txt"])
                    
                    if st.form_submit_button("🚀 Submit to Singularity"):
                        if not name or not email or not resume_file:
                            st.warning("Please provide all required neural data.")
                        else:
                            with st.spinner("Injecting into recruitment nervous system..."):
                                files = {"file": (resume_file.name, resume_file.read(), resume_file.type)}
                                data = {"name": name, "email": email}
                                try:
                                    post_res = requests.post(
                                        f"{api_url}/public/apply/{job['id']}", 
                                        data=data, 
                                        files=files
                                    )
                                    if post_res.status_code == 200:
                                        res_json = post_res.json()
                                        st.markdown(f"""
                                            <div style="background: rgba(16, 185, 129, 0.2); border: 1px solid #10B981; padding: 1.5rem; border-radius: 12px; margin: 1rem 0;">
                                                <h3 style="margin: 0; color: #10B981;">🚀 Application Synchronized!</h3>
                                                <p style="margin: 5px 0 0 0;">System Match Probability: <b>{res_json.get('match_score')}%</b></p>
                                            </div>
                                        """, unsafe_allow_html=True)
                                        st.balloons()
                                        time.sleep(2)
                                        st.session_state.applying_for_id = None
                                        st.rerun()
                                    else:
                                        st.error(f"Ingestion failed: {post_res.text}")
                                except Exception as e:
                                    st.error(f"Gateway error: {e}")
                
                if st.button("Cancel & Close", key=f"cancel_{job['id']}"):
                    st.session_state.applying_for_id = None
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            st.write("") # Spacer
