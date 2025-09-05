import streamlit as st
from PIL import Image
from utils.streamlit_utils import hide_icons, hide_sidebar, remove_whitespaces
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
hide_icons()
hide_sidebar()
remove_whitespaces()

# Main title
st.title("Certificate Validation System")
st.markdown("### Blockchain-Powered Digital Certificate Management")

# Add some spacing
st.write("")
st.write("")

# About section
st.markdown("""
**About This System:** This platform uses blockchain technology to generate, store, and verify digital certificates securely. 
Certificates are stored on IPFS (InterPlanetary File System) and verified through Ethereum smart contracts.
""")

st.write("")
st.write("")

# Role selection section
st.markdown("## Select Your Role")
st.markdown("Choose how you want to interact with the certificate system")

# Create two columns for role selection
col1, col2 = st.columns(2)

# Try to load images, with fallback if they don't exist
try:
    institute_logo = Image.open("../assets/institute_logo.png")
    institute_image = institute_logo
except:
    institute_image = None

try:
    company_logo = Image.open("../assets/company_logo.jpg")
    verifier_image = company_logo
except:
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

# Handle button clicks
if clicked_institute:
    st.session_state.profile = "Institute"
    switch_page('login')
elif clicked_verifier:
    st.session_state.profile = "Verifier"
    switch_page('login')

# Add footer
st.write("")
st.write("")
st.markdown("---")
st.markdown("*Powered by Blockchain Technology • IPFS Storage • Ethereum Smart Contracts*")
