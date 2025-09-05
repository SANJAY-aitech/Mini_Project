# Certificate Validation System

A blockchain-based system for generating and verifying digital certificates using Ethereum smart contracts and IPFS storage.

## Quick Start


### Local Setup

#### Prerequisites
- Node.js (version 16 or higher)
- Python (version 3.9 or higher)
- Git

#### Installation Steps

1. **Install required packages:**
   ```bash
   npm install -g truffle ganache-cli
   pip install -r application/requirements.txt
   ```

2. **Create a `.env` file** in the project root with your API keys:
   ```
   PINATA_API_KEY = "your_pinata_api_key"
   PINATA_API_SECRET = "your_pinata_secret_key"
   FIREBASE_API_KEY = "your_firebase_api_key"
   FIREBASE_AUTH_DOMAIN = "your_firebase_auth_domain"
   FIREBASE_DATABASE_URL = ""
   FIREBASE_PROJECT_ID = "your_firebase_project_id"
   FIREBASE_STORAGE_BUCKET = "your_firebase_storage_bucket"
   FIREBASE_MESSAGING_SENDER_ID = "your_firebase_messaging_sender_id"
   FIREBASE_APP_ID = "your_firebase_app_id"
   institute_email = "institute@gmail.com"
   institute_password = "123456"
   ```

3. **Start the blockchain:**
   ```bash
   ganache-cli -h 127.0.0.1 -p 8545
   ```

4. **Deploy smart contracts:**
   ```bash
   truffle migrate
   ```

5. **Run the application:**
   ```bash
   cd application
   streamlit run app.py
   ```

6. **Open your browser** and go to: http://localhost:8501

## How to Use

1. **Login as Institute** to generate certificates
2. **Login as Verifier** to verify certificates
3. **Upload certificate PDFs** or enter certificate IDs for verification

## Features

- Generate digital certificates with blockchain verification
- Store certificates on IPFS (decentralized storage)
- Verify certificates using PDF upload or certificate ID
- User authentication with Firebase
- Web interface built with Streamlit
