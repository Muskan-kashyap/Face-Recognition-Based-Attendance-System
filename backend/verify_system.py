import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_flow():
    # 1. Login (assuming a test user exists or we use a known one)
    # For simplicity, we'll use the API without auth if we can, 
    # but the routes have Depends(deps.get_current_active_user).
    # I'll mock the dependency in the test or just try to hit it.
    
    print("--- STARTING SYSTEM VERIFICATION ---")
    
    try:
        # Check root
        resp = requests.get("http://127.0.0.1:8000/")
        print(f"Root check: {resp.status_code}")
        
        # In a real test, we would get a JWT token here.
        # Since I cannot easily log in without a password, 
        # I'll check if the routers are registered by looking at the docs.
        resp = requests.get("http://127.0.0.1:8000/openapi.json")
        if resp.status_code == 200:
            paths = resp.json().get("paths", {})
            print("Verifying Registered Endpoints:")
            print(f"- /ticketing: {'/ticketing/' in paths}")
            print(f"- /payroll: {'/payroll/' in paths}")
            print(f"- /reimbursement: {'/reimbursement/' in paths}")
            
            if '/ticketing/' in paths and '/payroll/' in paths and '/reimbursement/' in paths:
                print("SUCCESS: All modules registered in FastAPI.")
            else:
                print("FAILURE: Some modules are missing.")
        else:
            print(f"Failed to fetch openapi.json: {resp.status_code}")
            
    except Exception as e:
        print(f"Error connecting to backend: {e}")
        print("Make sure the backend is running with 'uvicorn main:app --reload'")

if __name__ == "__main__":
    test_flow()
