import streamlit as st
import os
import hashlib
from utils.cert_utils import extract_certificate
from utils.streamlit_utils import view_certificate
from connection import contract
from utils.streamlit_utils import displayPDF, hide_icons, hide_sidebar, remove_whitespaces
from streamlit_extras.switch_page_button import switch_page

# Check login state
if 'verifier_logged_in' not in st.session_state or not st.session_state['verifier_logged_in']:
    st.title("Verifier Access")
    st.write("")
    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Register as New User", key="register_btn", use_container_width=True):
            switch_page("register")
    with col2:
        if st.button("🔐 Already Have an Account? Login", key="login_btn", use_container_width=True):
            switch_page("login")
    st.stop()

# --- Verifier Dashboard (only shown if logged in) ---
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
hide_icons()
hide_sidebar()
remove_whitespaces()


st.markdown("## Verifier Dashboard")
options = ("Verify Certificate using PDF", "View/Verify Certificate using Certificate ID")
selected = st.selectbox("Select an option", options)

if selected == options[0]:
    st.markdown("### Verify Certificate using PDF")
    uploaded_file = st.file_uploader("Upload the PDF version of the certificate")
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        with open("certificate.pdf", "wb") as file:
            file.write(bytes_data)
        try:
            (uid, candidate_name, course_name, org_name, embedded_hash) = extract_certificate("certificate.pdf")
            st.write(f"[DEBUG] Verification Extracted UID: {uid}")
            st.write(f"[DEBUG] Verification Extracted Name: {candidate_name}")
            st.write(f"[DEBUG] Verification Extracted Course: {course_name}")
            st.write(f"[DEBUG] Verification Extracted Org: {org_name}")
            st.write(f"[DEBUG] Embedded hash found in PDF: {embedded_hash}")
            displayPDF("certificate.pdf")
            os.remove("certificate.pdf")

            
            # Prefer embedded certificate hash from PDF when available
            if embedded_hash:
                certificate_id = embedded_hash
                st.write(f"[DEBUG] Using embedded certificate hash from PDF: {certificate_id}")
            else:
                # Fallback: recompute from extracted fields
                data_to_hash = f"{uid}{candidate_name}{course_name}{org_name}".encode('utf-8')
                certificate_id = hashlib.sha256(data_to_hash).hexdigest()
                st.write(f"[DEBUG] Recomputed Verification Generated Hash: {certificate_id}")

            # Debug blockchain verification
            st.write(f"[DEBUG] Checking certificate on blockchain with ID: {certificate_id}")
            result = contract.functions.isVerified(certificate_id).call()
            st.write(f"[DEBUG] Blockchain verification result: {result}")
            
            if not result:
                st.error("Certificate verification failed. Possible reasons:")
                st.write("1. Certificate ID not found on blockchain")
                st.write("2. Extracted data might differ from registration data")
                st.write("3. PDF format might have changed")
                
                # Try to get registered certificate data for comparison
                try:
                    registered_data = contract.functions.getCertificate(certificate_id).call()
                    st.write("\nRegistered certificate data:")
                    st.write(f"UID: {registered_data[0]}")
                    st.write(f"Name: {registered_data[1]}")
                    st.write(f"Course: {registered_data[2]}")
                    st.write(f"Organization: {registered_data[3]}")
                except Exception as e:
                    st.write("\nNo registered certificate found with this ID")
            if result:
                st.success("Certificated validated successfully!")
            else:
                st.error("Invalid Certificate! Certificate might be tampered")
        except Exception as e:
            st.error("Invalid Certificate! Certificate might be tampered")

elif selected == options[1]:
    st.markdown("### View/Verify Certificate using Certificate ID")
    form = st.form("Validate-Certificate")
    certificate_id = form.text_input("Enter the Certificate ID")
    submit = form.form_submit_button("Validate")
    if submit:
        if not certificate_id:
            st.error("Please enter a Certificate ID")
            st.stop()
            
        try:
            # First verify on blockchain
            result = contract.functions.isVerified(certificate_id).call()
            if not result:
                st.error("❌ Certificate ID not found on blockchain")
                st.stop()
                
            # If verified on blockchain, try to fetch and display
            st.write(f"[DEBUG] Attempting to verify certificate: {certificate_id}")
            if view_certificate(certificate_id):
                st.success("✅ Certificate verified successfully!")
            else:
                st.error("❌ Certificate found on blockchain but could not be retrieved")
                st.info("This could be due to:")
                st.write("1. IPFS gateway connection issues")
                st.write("2. Certificate file may no longer be available on IPFS")
                st.write("3. Pinata API rate limiting")
                
        except Exception as e:
            st.error("❌ Error during verification")
            st.write(f"[DEBUG] Error details: {str(e)}")


st.write("")
st.write("")
if st.button("⬅️ Back to Home", key="back_btn", use_container_width=True):
    switch_page("app")