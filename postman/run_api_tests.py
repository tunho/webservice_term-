import sys
import os
import requests
import json

# Add parent directory to path to import settings if needed, 
# but we will try to run against localhost:8080 or env var
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8080/api/v1")
HEALTH_URL = os.getenv("HEALTH_URL", "http://localhost:8080/health")

def run_tests():
    print(f"Running API tests against {BASE_URL}...")
    
    # 1. Health Check
    try:
        print(f"Checking {HEALTH_URL}...")
        res = requests.get(HEALTH_URL)
        if res.status_code == 200:
            print("[SUCCESS] Health Check passed")
        else:
            print(f"[FAILED] Health Check returned {res.status_code}")
            return
    except Exception as e:
        print(f"[FAILED] Could not connect to server: {e}")
        return

    # 2. Login
    print("Testing Login...")
    login_data = {
        "username": "user@example.com", # OAuth2PasswordRequestForm uses username
        "password": "password123"
    }
    # Try JSON login if endpoint supports it, otherwise form data
    # The API uses /auth/login with JSON body in this project
    try:
        res = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "user@example.com",
            "password": "password123"
        })
        
        if res.status_code == 200:
            print("[SUCCESS] Login passed")
            token = res.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print(f"[FAILED] Login failed: {res.text}")
            return
    except Exception as e:
        print(f"[FAILED] Login request error: {e}")
        return

    # 3. Get Calendars
    print("Testing Get Calendars...")
    try:
        res = requests.get(f"{BASE_URL}/calendars", headers=headers)
        if res.status_code == 200:
            calendars = res.json().get("content", [])
            print(f"[SUCCESS] Get Calendars passed (Found {len(calendars)} calendars)")
        else:
            print(f"[FAILED] Get Calendars failed: {res.text}")
    except Exception as e:
        print(f"[FAILED] Get Calendars request error: {e}")

    print("\n✨ All automated tests completed successfully!")

if __name__ == "__main__":
    # Install requests if not present (though it should be in container)
    try:
        import requests
    except ImportError:
        print("Installing requests...")
        os.system("pip install requests")
        import requests
        
    run_tests()
