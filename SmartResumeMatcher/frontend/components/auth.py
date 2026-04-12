import streamlit as st
import requests

def render_auth_ui(API_URL):
    st.markdown(
        """<div style="text-align: center; padding: 4rem 0 2rem 0;">
            <h2 style="font-family: 'Outfit'; font-size: 3rem; font-weight: 900; margin-bottom: 0.5rem; background: linear-gradient(to right, #FFF, #6366F1); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Secure Access</h2>
            <p style="color: #64748B; font-size: 1.1rem;">Enterprise Recruitment Intelligence Portal</p>
        </div>""", 
        unsafe_allow_html=True
    )
    
    login_container = st.container()
    with login_container:
        st.markdown('<div class="modern-card" style="max-width: 480px; margin: 0 auto;">', unsafe_allow_html=True)
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
                res = requests.post(f"{API_URL}/auth/token", data={"username": login_email, "password": login_password})
                if res.status_code == 200:
                    st.session_state.token = res.json()["access_token"]
                    u_res = requests.get(f"{API_URL}/auth/me", headers={"Authorization": f"Bearer {st.session_state.token}"})
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
                res = requests.post(f"{API_URL}/auth/register", json={"email": reg_email, "username": reg_username, "password": reg_password})
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
