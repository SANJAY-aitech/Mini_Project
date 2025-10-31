import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import os
from PIL import Image
from utils.streamlit_utils import hide_icons, hide_sidebar, remove_whitespaces

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
hide_icons()
hide_sidebar()
remove_whitespaces()


st.title("Certificate Validation System")
st.markdown("### Blockchain-Powered Digital Certificate Management")


st.write("")
st.write("")



st.write("")
st.write("")

st.markdown("## Select Your Role")
st.markdown("Choose how you want to interact with the certificate system")


col1, col2 = st.columns(2)


try:
    institute_path = os.path.join("..", "assets", "institute_logo.png")
    institute_logo = Image.open(institute_path)
    institute_image = institute_logo
except Exception:
    institute_image = None

try:
    company_path = os.path.join("..", "assets", "company_logo.jpg")
    company_logo = Image.open(company_path)
    verifier_image = company_logo
except Exception:
    verifier_image = None

with col1:
    st.markdown("### 🏛️ Institute")
    st.markdown("Generate and issue digital certificates to students")
    
    if institute_image:
        st.image(institute_image, output_format="PNG", width=200)
    
    clicked_institute = st.button("Login as Institute", key="institute_btn")

with col2:
    st.markdown("### 🔍 Verifier")
    st.markdown("Verify the authenticity of digital certificates")
    
    if verifier_image:
        st.image(verifier_image, output_format="JPEG", width=200)
    
    clicked_verifier = st.button("Login as Verifier", key="verifier_btn")


if clicked_institute:
    st.session_state.profile = "Institute"
    switch_page("institute")
elif clicked_verifier:
    st.session_state.profile = "Verifier"
    switch_page("verifier")


st.write("")
st.write("")
st.markdown("---")
