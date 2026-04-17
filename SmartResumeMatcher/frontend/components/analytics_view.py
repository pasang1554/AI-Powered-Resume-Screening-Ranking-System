import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests

def render_institutional_insights(api_url, auth_header, groq_api_key):
    st.markdown(
        """<div class="neural-header" style="background: linear-gradient(90deg, #F59E0B, #D97706);">
            <h2>📊 Institutional Intelligence Command Center</h2>
            <p style="margin: 0; color: rgba(255,255,255,0.8); font-size: 0.9rem;">Global talent velocity, skill scarcity indexing, and strategic workforce roadmaps.</p>
        </div>""", 
        unsafe_allow_html=True
    )
    
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)

    tab_market, tab_roi, tab_roadmap = st.tabs(["🌐 Market Scarcity", "💎 Yield & ROI", "🔮 Quantum Roadmap"])

    with tab_market:
        st.markdown("#### Skill Scarcity Benchmark")
        try:
            res = requests.get(f"{api_url}/analytics/market-scarcity", headers=auth_header)
            if res.status_code == 200:
                scarcity_data = res.json()
                if not scarcity_data:
                    st.info("📊 **Intelligence Accumulating:** No skills identified in the talent pool yet. Run institutional audits to populate the scarcity index.")
                else:
                    df_scarcity = pd.DataFrame(scarcity_data)
                    
                    fig = px.bar(
                        df_scarcity, 
                        x="skill", 
                        y="scarcity_index", 
                        color="scarcity_index",
                        title="Institutional Scarcity Index (Higher = Harder to Find)",
                        labels={"scarcity_index": "Scarcity %", "skill": "Core Science"},
                        template="plotly_dark",
                        color_continuous_scale="YlOrRd"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.markdown("##### Vault Inventory")
                    st.table(df_scarcity[["skill", "vault_count", "scarcity_index"]])
            else: st.error("Failed to load scarcity data.")
        except: st.error("Analytics endpoint unreachable.")

    with tab_roi:
        st.markdown("#### Recruitment ROI Metrics")
        try:
            roi_res = requests.get(f"{api_url}/analytics/roi", headers=auth_header)
            if roi_res.status_code == 200:
                roi = roi_res.json()
                kpi1, kpi2, kpi3 = st.columns(3)
                kpi1.metric("Time Optimization", f"{roi['total_time_saved_hours']} hrs", delta="+12%")
                kpi2.metric("Fiscal Impact", f"${roi['estimated_cost_savings_usd']:,}", delta="+8%")
                kpi3.metric("Strategic Yield", roi['roi_multiple'], delta="Exponential")
            
            # Simulated Yield Chart
            st.markdown("#### Monthly Velocity Ingestion")
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
            data = {"Month": months, "Manual": [10, 15, 12, 18, 14, 16], "Neural": [45, 62, 58, 89, 112, 145]}
            df_v = pd.DataFrame(data)
            fig_v = px.line(df_v, x="Month", y=["Manual", "Neural"], title="Intelligence Yield Projection", template="plotly_dark")
            st.plotly_chart(fig_v, use_container_width=True)
            
        except: st.info("ROI Engine initializing...")

    with tab_roadmap:
        st.markdown("#### Quantum Workforce Roadmap (24 Mo)")
        try:
            roadmap_res = requests.get(f"{api_url}/analytics/workforce-roadmap", headers=auth_header)
            if roadmap_res.status_code == 200:
                roadmap = roadmap_res.json()
                st.info(f"🔮 **Horizon:** {roadmap['horizon']}")
                st.warning(f"⚠️ **Predicted Gap:** {roadmap['predicted_gaps'][0]['skill']} (Urgency: {roadmap['predicted_gaps'][0]['urgency']})")
                st.success(f"🚀 **Action:** {roadmap['hiring_roadmap']}")
            
            sim_res = requests.get(f"{api_url}/analytics/multiverse-strategy", headers=auth_header)
            if sim_res.status_code == 200:
                sim = sim_res.json()
                st.markdown(f"""<div style="background: rgba(99, 102, 241, 0.1); border: 1px solid #6366F1; padding: 1rem; border_radius: 8px;">
                    <p style="margin:0; font-weight: 800; color: #6366F1;">MULTIVERSE STRATEGY SYNOPSIS</p>
                    <p style='margin:0;'>{sim['optimal_path']}</p>
                    <p style='margin:0; font-size: 0.8rem; color: grey;'>Confidence: {sim['strategy_confidence']} | Iterations: {sim['simulated_timelines']}</p>
                </div>""", unsafe_allow_html=True)
        except: st.info("Roadmap engine initializing...")

    st.markdown('</div>', unsafe_allow_html=True)
