import streamlit as st
from db.firebase_app import login
from dotenv import load_dotenv
import os
from streamlit_extras.switch_page_button import switch_page
from utils.streamlit_utils import hide_icons, hide_sidebar, remove_whitespaces

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
hide_icons()
hide_sidebar()
remove_whitespaces()

load_dotenv()

# Main title
profile_type = "Institute" if st.session_state.profile == "Institute" else "Verifier"
st.title(f"Login as {profile_type}")
st.markdown("### Enter your credentials to access the system")

# Add some spacing
st.write("")
st.write("")

# Login form
st.markdown("### 🔐 Authentication")

# Create form with custom styling
form = st.form("login")

# Add form fields
email = form.text_input("Email Address", key="email_input")
password = form.text_input("Password", type="password", key="password_input")

# Add some spacing
st.write("")
st.write("")

# Submit button
submit = form.form_submit_button("🚀 Login", use_container_width=True)

# Registration link for verifiers
if st.session_state.profile != "Institute":
    st.write("")
    st.markdown("Don't have an account?")
    
    clicked_register = st.button("📝 Create New Account", key="register_btn", use_container_width=True)

    if clicked_register:
        switch_page("register")

# Handle form submission
if submit:
    if st.session_state.profile == "Institute":
        valid_email = os.getenv("institute_email")
        valid_pass = os.getenv("institute_password")
        if email == valid_email and password == valid_pass:
            st.success("✅ Login successful! Redirecting...")
            switch_page("institute")
        else:
            st.error("❌ Invalid credentials! Please check your email and password.")
    else:
        result = login(email, password)
        if result == "success":
            st.session_state['verifier_logged_in'] = True
            st.success("✅ Login successful! Redirecting...")
            switch_page("verifier")
        else:
            st.error("❌ Invalid credentials! Please check your email and password.")

# Add back button
st.write("")
st.write("")
st.markdown("Need to change your role?")

if st.button("⬅️ Back to Home", key="back_btn", use_container_width=True):
    switch_page("app")
        