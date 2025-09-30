import streamlit as st
from db.firebase_app import register
from streamlit_extras.switch_page_button import switch_page
from utils.streamlit_utils import hide_icons, hide_sidebar, remove_whitespaces

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
hide_icons()
hide_sidebar()
remove_whitespaces()

# Main title
st.title("Create New Account")
st.markdown("### Join our blockchain certificate verification system")

# Add some spacing
st.write("")
st.write("")

# Registration form
st.markdown("### 📝 Registration")

# Create form with custom styling
form = st.form("register")

# Add form fields
email = form.text_input("Email Address", placeholder="Enter your email address", key="reg_email_input")
password = form.text_input("Password", type="password", placeholder="Create a strong password", key="reg_password_input")

# Add some spacing
st.write("")
st.write("")

# Submit button
submit = form.form_submit_button("🚀 Create Account", use_container_width=True)

# Login link
st.write("")
st.markdown("Already have an account?")

clicked_login = st.button("🔐 Sign In Instead", key="login_btn", use_container_width=True)

if clicked_login:
    switch_page("login")
    
# Handle form submission
if submit:
    if email and password:
        result = register(email, password)
        if result == "success":
            st.session_state['verifier_logged_in'] = True
            st.success("✅ Registration successful! Welcome to the system.")
            if st.session_state.profile == "Institute":
                switch_page("institute")
            else:
                switch_page("verifier")
        else:
            st.error("❌ Registration failed! Please try again with different credentials.")
    else:
        st.error("❌ Please fill in all fields!")

# Add back button
st.write("")
st.write("")
st.markdown("Changed your mind?")

if st.button("⬅️ Back to Home", key="back_btn", use_container_width=True):
    switch_page("app")