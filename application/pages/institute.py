import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv
import hashlib
from utils.cert_utils import generate_certificate, generate_bulk_certificates, validate_certificate_data
from utils.streamlit_utils import view_certificate
from connection import contract, w3
from utils.streamlit_utils import hide_icons, hide_sidebar, remove_whitespaces
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
hide_icons()
hide_sidebar()
remove_whitespaces()

load_dotenv()

api_key = os.getenv("PINATA_API_KEY")
api_secret = os.getenv("PINATA_API_SECRET")


def upload_to_pinata(file_path, api_key, api_secret):
    # Set up the Pinata API endpoint and headers
    pinata_api_url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {
        "pinata_api_key": api_key,
        "pinata_secret_api_key": api_secret,
    }

    # Prepare the file for upload
    with open(file_path, "rb") as file:
        files = {"file": (file.name, file)}

        # Make the request to Pinata
        response = requests.post(pinata_api_url, headers=headers, files=files)

        # Parse the response
        result = json.loads(response.text)

        if "IpfsHash" in result:
            ipfs_hash = result["IpfsHash"]
            print(f"File uploaded to Pinata. IPFS Hash: {ipfs_hash}")
            return ipfs_hash
        else:
            print(f"Error uploading to Pinata: {result.get('error', 'Unknown error')}")
            return None


st.markdown("## 🏛️ Institute Dashboard")
st.markdown("### Welcome to the Certificate Management System")

# Create tabs for better organization
tab1, tab2, tab3, tab4 = st.tabs(["📜 Generate Certificate", "📋 Bulk Generate", "🔍 View Certificates", "📊 Certificate Analytics"])

with tab1:
    st.markdown("### Generate New Certificate")
    st.markdown("Fill in the details below to generate and upload a certificate to the blockchain.")
    
    # Enhanced form with better styling
    with st.form("Generate-Certificate", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            uid = st.text_input(
                label="Student UID", 
                placeholder="Enter unique student identifier",
                help="This should be a unique identifier for the student"
            )
            candidate_name = st.text_input(
                label="Student Name", 
                placeholder="Enter full name of the student",
                help="Full name as it should appear on the certificate"
            )
        
        with col2:
            course_name = st.text_input(
                label="Course Name", 
                placeholder="Enter course/program name",
                help="Name of the course or program completed"
            )
            org_name = st.text_input(
                label="Organization Name", 
                placeholder="Enter your institution name",
                help="Name of your educational institution"
            )
        
        # Additional options
        st.markdown("#### Certificate Options")
        col3, col4 = st.columns(2)
        
        with col3:
            include_logo = st.checkbox("Include Institution Logo", value=True)
            certificate_format = st.selectbox("Certificate Format", ["PDF", "PNG", "JPG"], index=0)
        
        with col4:
            auto_generate_id = st.checkbox("Auto-generate Certificate ID", value=True)
            blockchain_upload = st.checkbox("Upload to Blockchain", value=True)
        
        # Submit button with enhanced styling
        submit = st.form_submit_button(
            "🚀 Generate & Upload Certificate", 
            use_container_width=True,
            type="primary"
        )
        
        if submit:
            # Validation
            if not all([uid, candidate_name, course_name, org_name]):
                st.error("❌ Please fill in all required fields!")
            else:
                # Show progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Step 1: Generate certificate
                    status_text.text("📄 Generating certificate PDF...")
                    progress_bar.progress(20)
                    
                    pdf_file_path = f"certificate_{uid}_{candidate_name.replace(' ', '_')}.pdf"
                    institute_logo_path = "../assets/logo.jpg" if include_logo else None
                    
                    generate_certificate(pdf_file_path, uid, candidate_name, course_name, org_name, institute_logo_path)
                    
                    # Step 2: Upload to IPFS
                    if blockchain_upload:
                        status_text.text("☁️ Uploading to IPFS...")
                        progress_bar.progress(50)
                        
                        if not api_key or not api_secret:
                            st.error("❌ Pinata API credentials not configured. Please check your .env file.")
                            st.stop()
                            
                        ipfs_hash = upload_to_pinata(pdf_file_path, api_key, api_secret)
                        
                        if ipfs_hash is None:
                            st.error("❌ Failed to upload certificate to IPFS. Please check your Pinata API credentials and try again.")
                        else:
                            # Step 3: Generate certificate ID
                            status_text.text("🔐 Generating certificate ID...")
                            progress_bar.progress(70)
                            
                            if auto_generate_id:
                                data_to_hash = f"{uid}{candidate_name}{course_name}{org_name}".encode('utf-8')
                                certificate_id = hashlib.sha256(data_to_hash).hexdigest()
                            else:
                                certificate_id = st.text_input("Enter custom Certificate ID")
                            
                            # Step 4: Upload to blockchain
                            status_text.text("⛓️ Uploading to blockchain...")
                            progress_bar.progress(90)
                            
                            try:
                                contract.functions.generateCertificate(
                                    certificate_id, uid, candidate_name, course_name, org_name, ipfs_hash
                                ).transact({'from': w3.eth.accounts[0]})
                                
                                progress_bar.progress(100)
                                status_text.text("✅ Certificate successfully generated!")
                                
                                # Success message with details
                                st.success("🎉 Certificate Successfully Generated and Uploaded!")
                                
                                # Display certificate details
                                st.markdown("### Certificate Details")
                                col_info1, col_info2 = st.columns(2)
                                
                                with col_info1:
                                    st.info(f"**Certificate ID:** `{certificate_id}`")
                                    st.info(f"**Student UID:** `{uid}`")
                                    st.info(f"**Student Name:** `{candidate_name}`")
                                
                                with col_info2:
                                    st.info(f"**Course:** `{course_name}`")
                                    st.info(f"**Organization:** `{org_name}`")
                                    st.info(f"**IPFS Hash:** `{ipfs_hash}`")
                                
                                # Download link for the certificate
                                with open(pdf_file_path, "rb") as file:
                                    st.download_button(
                                        label="📥 Download Certificate PDF",
                                        data=file.read(),
                                        file_name=pdf_file_path,
                                        mime="application/pdf"
                                    )
                                
                                # Clean up
                                os.remove(pdf_file_path)
                                
                            except Exception as e:
                                st.error(f"❌ Failed to generate certificate on blockchain: {str(e)}")
                    else:
                        # Just generate PDF without blockchain upload
                        progress_bar.progress(100)
                        status_text.text("✅ Certificate generated successfully!")
                        st.success("📄 Certificate PDF generated successfully!")
                        
                        with open(pdf_file_path, "rb") as file:
                            st.download_button(
                                label="📥 Download Certificate PDF",
                                data=file.read(),
                                file_name=pdf_file_path,
                                mime="application/pdf"
                            )
                        
                        os.remove(pdf_file_path)
                        
                except Exception as e:
                    st.error(f"❌ Error generating certificate: {str(e)}")
                    progress_bar.progress(0)
                    status_text.text("")

with tab2:
    st.markdown("### Bulk Certificate Generation")
    st.markdown("Upload a CSV file or manually enter multiple student records to generate certificates in bulk.")
    
    # Option selection
    bulk_option = st.radio(
        "Choose input method:",
        ["📁 Upload CSV File", "✏️ Manual Entry"],
        horizontal=True
    )
    
    if bulk_option == "📁 Upload CSV File":
        st.markdown("#### Upload CSV File")
        st.markdown("Upload a CSV file with columns: uid, candidate_name, course_name")
        
        uploaded_file = st.file_uploader(
            "Choose CSV file",
            type=['csv'],
            help="CSV should have columns: uid, candidate_name, course_name"
        )
        
        if uploaded_file is not None:
            try:
                import pandas as pd
                df = pd.read_csv(uploaded_file)
                
                # Display preview
                st.markdown("#### Data Preview")
                st.dataframe(df.head())
                
                # Validate columns
                required_columns = ['uid', 'candidate_name', 'course_name']
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    st.error(f"❌ Missing required columns: {', '.join(missing_columns)}")
                else:
                    # Organization name input
                    org_name = st.text_input("Organization Name", placeholder="Enter your institution name")
                    
                    if st.button("🚀 Generate Bulk Certificates", use_container_width=True):
                        if not org_name:
                            st.error("❌ Please enter organization name!")
                        else:
                            # Convert DataFrame to list of dictionaries
                            certificates_data = df[required_columns].to_dict('records')
                            
                            # Show progress
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            # Create output directory
                            output_dir = "bulk_certificates"
                            os.makedirs(output_dir, exist_ok=True)
                            
                            # Generate certificates
                            status_text.text("📄 Generating certificates...")
                            generated_certs = generate_bulk_certificates(
                                certificates_data, output_dir, org_name, "../assets/logo.jpg"
                            )
                            
                            # Show results
                            progress_bar.progress(100)
                            status_text.text("✅ Bulk generation completed!")
                            
                            # Display results
                            st.markdown("#### Generation Results")
                            
                            success_count = sum(1 for cert in generated_certs if cert['status'] == 'success')
                            error_count = len(generated_certs) - success_count
                            
                            col_result1, col_result2 = st.columns(2)
                            with col_result1:
                                st.success(f"✅ Successful: {success_count}")
                            with col_result2:
                                if error_count > 0:
                                    st.error(f"❌ Failed: {error_count}")
                            
                            # Show detailed results
                            results_df = pd.DataFrame(generated_certs)
                            st.dataframe(results_df)
                            
                            # Download successful certificates as zip
                            if success_count > 0:
                                import zipfile
                                zip_path = "certificates_bulk.zip"
                                
                                with zipfile.ZipFile(zip_path, 'w') as zipf:
                                    for cert in generated_certs:
                                        if cert['status'] == 'success' and cert['file_path']:
                                            zipf.write(cert['file_path'], os.path.basename(cert['file_path']))
                                
                                with open(zip_path, 'rb') as f:
                                    st.download_button(
                                        label="📥 Download All Certificates (ZIP)",
                                        data=f.read(),
                                        file_name=zip_path,
                                        mime="application/zip"
                                    )
                                
                                # Clean up
                                os.remove(zip_path)
                                for cert in generated_certs:
                                    if cert['file_path'] and os.path.exists(cert['file_path']):
                                        os.remove(cert['file_path'])
                                os.rmdir(output_dir)
                            
            except Exception as e:
                st.error(f"❌ Error processing CSV file: {str(e)}")
    
    else:  # Manual Entry
        st.markdown("#### Manual Entry")
        st.markdown("Add multiple student records manually")
        
        # Dynamic form for adding students
        if 'student_records' not in st.session_state:
            st.session_state.student_records = []
        
        # Add new student form
        with st.form("add_student"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                uid = st.text_input("Student UID", key="bulk_uid")
            with col2:
                name = st.text_input("Student Name", key="bulk_name")
            with col3:
                course = st.text_input("Course Name", key="bulk_course")
            
            add_student = st.form_submit_button("➕ Add Student")
            
            if add_student:
                if uid and name and course:
                    # Validate data
                    errors = validate_certificate_data(uid, name, course, "Temp Org")
                    if errors:
                        st.error(f"❌ Validation errors: {', '.join(errors)}")
                    else:
                        st.session_state.student_records.append({
                            'uid': uid,
                            'candidate_name': name,
                            'course_name': course
                        })
                        st.success(f"✅ Added student: {name}")
                        st.rerun()
                else:
                    st.error("❌ Please fill in all fields!")
        
        # Display current students
        if st.session_state.student_records:
            st.markdown("#### Current Student Records")
            
            # Create DataFrame for display
            import pandas as pd
            df_display = pd.DataFrame(st.session_state.student_records)
            st.dataframe(df_display, use_container_width=True)
            
            # Organization name and generate button
            org_name_manual = st.text_input("Organization Name", key="bulk_org")
            
            col_gen1, col_gen2 = st.columns([1, 1])
            
            with col_gen1:
                if st.button("🚀 Generate Certificates", use_container_width=True):
                    if not org_name_manual:
                        st.error("❌ Please enter organization name!")
                    else:
                        # Generate certificates
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        output_dir = "manual_certificates"
                        os.makedirs(output_dir, exist_ok=True)
                        
                        status_text.text("📄 Generating certificates...")
                        generated_certs = generate_bulk_certificates(
                            st.session_state.student_records, output_dir, org_name_manual, "../assets/logo.jpg"
                        )
                        
                        progress_bar.progress(100)
                        status_text.text("✅ Generation completed!")
                        
                        # Show results and download
                        success_count = sum(1 for cert in generated_certs if cert['status'] == 'success')
                        st.success(f"✅ Generated {success_count} certificates successfully!")
                        
                        if success_count > 0:
                            import zipfile
                            zip_path = "manual_certificates.zip"
                            
                            with zipfile.ZipFile(zip_path, 'w') as zipf:
                                for cert in generated_certs:
                                    if cert['status'] == 'success' and cert['file_path']:
                                        zipf.write(cert['file_path'], os.path.basename(cert['file_path']))
                            
                            with open(zip_path, 'rb') as f:
                                st.download_button(
                                    label="📥 Download Certificates (ZIP)",
                                    data=f.read(),
                                    file_name=zip_path,
                                    mime="application/zip"
                                )
                            
                            # Clean up
                            os.remove(zip_path)
                            for cert in generated_certs:
                                if cert['file_path'] and os.path.exists(cert['file_path']):
                                    os.remove(cert['file_path'])
                            os.rmdir(output_dir)
            
            with col_gen2:
                if st.button("🗑️ Clear All Records", use_container_width=True):
                    st.session_state.student_records = []
                    st.rerun()

with tab3:
    st.markdown("### View Existing Certificates")
    st.markdown("Enter a certificate ID to view its details and verify its authenticity.")
    
    with st.form("View-Certificate"):
        certificate_id = st.text_input(
            "Certificate ID", 
            placeholder="Enter the certificate ID to view",
            help="This is the unique identifier generated when the certificate was created"
        )
        
        col_view1, col_view2 = st.columns([1, 1])
        
        with col_view1:
            submit_view = st.form_submit_button("🔍 View Certificate", use_container_width=True)
        
        with col_view2:
            verify_cert = st.form_submit_button("✅ Verify Certificate", use_container_width=True)
        
        if submit_view or verify_cert:
            if not certificate_id:
                st.error("❌ Please enter a certificate ID!")
            else:
                try:
                    if submit_view:
                        view_certificate(certificate_id)
                    elif verify_cert:
                        # Enhanced verification
                        try:
                            is_verified = contract.functions.isVerified(certificate_id).call()
                            if is_verified:
                                st.success("✅ Certificate is verified and authentic!")
                                
                                # Get certificate details
                                uid, candidate_name, course_name, org_name, ipfs_hash = contract.functions.getCertificate(certificate_id).call()
                                
                                st.markdown("### Certificate Verification Details")
                                col_verify1, col_verify2 = st.columns(2)
                                
                                with col_verify1:
                                    st.info(f"**Student UID:** `{uid}`")
                                    st.info(f"**Student Name:** `{candidate_name}`")
                                
                                with col_verify2:
                                    st.info(f"**Course:** `{course_name}`")
                                    st.info(f"**Organization:** `{org_name}`")
                                
                                st.info(f"**IPFS Hash:** `{ipfs_hash}`")
                                st.info(f"**Blockchain Status:** ✅ Verified")
                                
                            else:
                                st.error("❌ Certificate not found or not verified!")
                        except Exception as e:
                            st.error(f"❌ Error verifying certificate: {str(e)}")
                            
                except Exception as e:
                    st.error("❌ Invalid Certificate ID or certificate not found!")

with tab4:
    st.markdown("### Certificate Analytics")
    st.markdown("View statistics and analytics about your certificates.")
    
    # Sample analytics (in a real system, this would come from database)
    col_stats1, col_stats2, col_stats3 = st.columns(3)
    
    with col_stats1:
        st.metric("Total Certificates", "📊 0", "0")
    
    with col_stats2:
        st.metric("This Month", "📈 0", "0")
    
    with col_stats3:
        st.metric("Success Rate", "✅ 100%", "0%")
    
    st.markdown("#### Certificate Generation Tips")
    
    col_tip1, col_tip2 = st.columns(2)
    
    with col_tip1:
        st.info("""
        **💡 Best Practices:**
        - Use unique UIDs for each student
        - Keep course names descriptive
        - Include institution logo for authenticity
        - Verify certificates after generation
        """)
    
    with col_tip2:
        st.info("""
        **🔧 Technical Notes:**
        - Certificates are stored on IPFS
        - Blockchain verification ensures authenticity
        - PDF format recommended for printing
        - Bulk generation saves time
        """)
    
    st.markdown("#### System Information")
    
    # Display system info
    system_info = {
        "Blockchain Network": "Ethereum (Local)",
        "IPFS Provider": "Pinata",
        "Certificate Format": "PDF",
        "Smart Contract": "Certification.sol",
        "Storage": "Decentralized (IPFS + Blockchain)"
    }
    
    for key, value in system_info.items():
        st.text(f"{key}: {value}")
    
    st.markdown("#### Recent Activity")
    st.info("📝 Certificate analytics feature coming soon! This will show detailed statistics about certificate generation and verification.")

# Add navigation
st.write("")
st.write("")
st.markdown("---")
if st.button("⬅️ Back to Home", key="back_btn", use_container_width=True):
    switch_page("app")
        
