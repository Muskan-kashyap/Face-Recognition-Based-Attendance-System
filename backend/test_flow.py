import requests
import numpy as np

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_flow():
    # 1. Login to get token
    print("Logging in...")
    resp = requests.post(f"{BASE_URL}/auth/login/access-token", data={
        "username": "admin",
        "password": "admin123"
    })
    if resp.status_code != 200:
        print(f"Login failed: {resp.status_code} - {resp.text}")
        return
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Logged in.")

    # 2. Get my profile to get user_id
    print("Getting profile...")
    resp = requests.get(f"{BASE_URL}/users/me", headers=headers)
    user_id = resp.json()["id"]
    print(f"User ID: {user_id}")

    # 3. Enroll a dummy face
    print("Enrolling face...")
    dummy_embedding = np.random.rand(128).tolist()
    resp = requests.post(
        f"{BASE_URL}/users/{user_id}/enroll", 
        json={"face_embedding": dummy_embedding},
        headers=headers
    )
    print(resp.json())

    # 4. Test identification (check-in with embedding only)
    print("Testing identification...")
    resp = requests.post(
        f"{BASE_URL}/attendance/check-in",
        json={
            "face_embedding": dummy_embedding,
            "source": "edge"
        }
    )
    print("Check-in Response:", resp.json())

if __name__ == "__main__":
    test_flow()
