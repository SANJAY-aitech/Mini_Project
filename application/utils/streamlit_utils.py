import streamlit as st
import base64
import requests
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from connection import contract


def displayPDF(file):

    with open(file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'


    st.markdown(pdf_display, unsafe_allow_html=True)


def view_certificate(certificate_id):
    try:
        # Get certificate data from blockchain
        result = contract.functions.getCertificate(certificate_id).call()
        ipfs_hash = result[4]
        
        st.write(f"[DEBUG] Retrieved IPFS hash from blockchain: {ipfs_hash}")
        
        # Construct Pinata gateway URL
        pinata_gateway_base_url = 'https://gateway.pinata.cloud/ipfs'
        content_url = f"{pinata_gateway_base_url}/{ipfs_hash}"
        st.write(f"[DEBUG] Attempting to fetch from Pinata: {content_url}")
        
        # Fetch PDF from Pinata with proper headers
        headers = {
            'Accept': 'application/pdf',
            'User-Agent': 'Mozilla/5.0'
        }
        response = requests.get(content_url, headers=headers)
        
        if response.status_code != 200:
            st.error(f"Failed to fetch certificate from IPFS. Status code: {response.status_code}")
            st.write(f"[DEBUG] Pinata response: {response.text[:200]}...")  # Show first 200 chars of error
            return False
            
        # Save and display PDF
        with open("temp.pdf", 'wb') as pdf_file:
            pdf_file.write(response.content)
        displayPDF("temp.pdf")
        os.remove("temp.pdf")
        return True
        
    except Exception as e:
        st.error(f"Error retrieving certificate: {str(e)}")
        return False


def hide_icons():
    hide_st_style = """
				<style>
				#MainMenu {visibility: hidden;}
				footer {visibility: hidden;}
				</style>"""
    st.markdown(hide_st_style, unsafe_allow_html=True)


def hide_sidebar():
    no_sidebar_style = """
    			<style>
        		div[data-testid="stSidebarNav"] {visibility: hidden;}
    			</style>"""
    st.markdown(no_sidebar_style, unsafe_allow_html=True)


def remove_whitespaces():
    st.markdown("""
        <style>
               .css-18e3th9 {
                    padding-top: 0rem;
                    padding-bottom: 10rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
               .css-1d391kg {
                    padding-top: 3.5rem;
                    padding-right: 1rem;
                    padding-bottom: 3.5rem;
                    padding-left: 1rem;
                }
        </style>""", unsafe_allow_html=True)
