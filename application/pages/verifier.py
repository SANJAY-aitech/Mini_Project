import streamlit as st
import os
import hashlib
from utils.cert_utils import extract_certificate
from utils.streamlit_utils import view_certificate
from connection import contract
from utils.streamlit_utils import displayPDF, hide_icons, hide_sidebar, remove_whitespaces
from streamlit_extras.switch_page_button import switch_page

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
            (uid, candidate_name, course_name, org_name) = extract_certificate("certificate.pdf")
            displayPDF("certificate.pdf")
            os.remove("certificate.pdf")

            # Calculating hash
            data_to_hash = f"{uid}{candidate_name}{course_name}{org_name}".encode('utf-8')
            certificate_id = hashlib.sha256(data_to_hash).hexdigest()

            # Smart Contract Call
            result = contract.functions.isVerified(certificate_id).call()
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
        try:
            view_certificate(certificate_id)
            # Smart Contract Call
            result = contract.functions.isVerified(certificate_id).call()
            if result:
                st.success("Certificated validated successfully!")
            else:
                st.error("Invalid Certificate ID!")
        except Exception as e:
            st.error("Invalid Certificate ID!")

# Add navigation
st.write("")
st.write("")
if st.button("⬅️ Back to Home", key="back_btn", use_container_width=True):
    switch_page("app")