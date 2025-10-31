import sys
import os
# Ensure application directory is on path so we can import connection
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR)

try:
    from connection import contract
except Exception as e:
    print("Error importing 'connection'. This usually means the contract ABI/address files are missing (build/contracts/Certification.json or deployment_config.json).")
    print("Please ensure you have run your Truffle migrations and that 'deployment_config.json' exists in the project root.")
    print("Example steps:")
    print("  1) Start Ganache or an Ethereum node: ganache-cli -h 127.0.0.1 -p 8545")
    print("  2) Run truffle migrate from the project root to generate build files and deployment_config.json")
    print("Then re-run this script.")
    print(f"Underlying error: {e}")
    sys.exit(2)

if len(sys.argv) < 2:
    print("Usage: python check_certificate.py <certificate_id>")
    sys.exit(1)

cert_id = sys.argv[1]
print(f"Checking certificate id: {cert_id}")

try:
    exists = contract.functions.isVerified(cert_id).call()
    print(f"isVerified: {exists}")
    if exists:
        data = contract.functions.getCertificate(cert_id).call()
        print("Registered certificate data:")
        print(f"  uid: {data[0]}")
        print(f"  candidate_name: {data[1]}")
        print(f"  course_name: {data[2]}")
        print(f"  org_name: {data[3]}")
        print(f"  ipfs_hash: {data[4]}")
    else:
        print("Certificate ID not found on-chain.")
except Exception as e:
    print(f"Error querying contract: {e}")
    sys.exit(2)
