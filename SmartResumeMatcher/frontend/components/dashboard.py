import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def render_analysis_dashboard(results):
    if not results:
        return

    df = pd.DataFrame(results)
    st.markdown(
        """<div style="background: linear-gradient(90deg, #6366F1, #4F46E5); padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;">
            <h2 style="margin: 0; color: white; display: flex; align-items: center; gap: 0.5rem;">
                📊 Neural Analytics Core
            </h2>
            <p style="margin: 0; color: rgba(255,255,255,0.8); font-size: 0.9rem;">Institutional intelligence retrieved from the Universal Talent Singularity.</p>
        </div>""", 
        unsafe_allow_html=True
    )
        
    # KPI Strategy Banner
    kpi_cols = st.columns(5)
    metrics = [
        (len(df), "Total Candidates"),
        (len(df[df["Status"] == "Shortlisted"]), "Shortlisted"),
        (f"{df['Score'].mean():.0f}%", "Avg Match"),
        (f"{df['ATS'].mean():.0f}%", "Avg ATS"),
        (f"{df['Experience'].mean():.1f}y", "Avg Exp"),
    ]
    
    for col, (val, label) in zip(kpi_cols, metrics):
        with col:
            st.markdown(
                f"""<div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 1.5rem; text-align: center;">
                    <div style="font-size: 2.5rem; font-weight: 900; color: #6366F1;">{val}</div>
                    <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.1em;">{label}</div>
                </div>""",
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Leaderboard and Charts
    tab_overview, tab_visuals = st.tabs(["🏆 Results Leaderboard", "📈 Neural Insights"])
    
    with tab_overview:
        # Simplified candidate table for readability
        display_cols = ["Rank", "Candidate", "Score", "ATS", "Experience", "Status"]
        existing_cols = [c for c in display_cols if c in df.columns]
        st.dataframe(df[existing_cols], use_container_width=True, hide_index=True)
        
    with tab_visuals:
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            fig_score = px.bar(df, x="Candidate", y="Score", color="Status", 
                             title="Match Score Distribution", template="plotly_dark")
            st.plotly_chart(fig_score, use_container_width=True)
        with col_chart2:
            fig_exp = px.scatter(df, x="Experience", y="Score", size="ATS", color="Status",
                               title="Experience vs. Score Analysis", template="plotly_dark")
            st.plotly_chart(fig_exp, use_container_width=True)
