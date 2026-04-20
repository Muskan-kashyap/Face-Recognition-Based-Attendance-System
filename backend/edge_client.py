import cv2
import face_recognition
import numpy as np
import os
import sys
import requests
from datetime import datetime

import math
import json
import threading
import time

# --- CONFIGURATION ---
BASE_URL = "http://127.0.0.1:8000/api/v1"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
OFFLINE_QUEUE_FILE = "offline_queue.json"

# --- Liveness Config ---
EYE_AR_THRESH = 0.25
EYE_AR_CONSEC_FRAMES = 3

def eye_aspect_ratio(eye):
    # eye is a list of (x, y) tuples
    # vertical distances
    A = math.sqrt((eye[1][0] - eye[5][0])**2 + (eye[1][1] - eye[5][1])**2)
    B = math.sqrt((eye[2][0] - eye[4][0])**2 + (eye[2][1] - eye[4][1])**2)
    # horizontal distance
    C = math.sqrt((eye[0][0] - eye[3][0])**2 + (eye[0][1] - eye[3][1])**2)
    ear = (A + B) / (2.0 * C)
    return ear


class AttendanceClient:
    def __init__(self):
        self.token = None
        self.session = requests.Session()
        self.offline_queue = self._load_queue()
        self.authenticate()
        self.blink_count = 0
        self.blink_counter = 0
        
        # Start Sync Thread
        self.sync_thread = threading.Thread(target=self._sync_worker, daemon=True)
        self.sync_thread.start()


    def _load_queue(self):
        if os.path.exists(OFFLINE_QUEUE_FILE):
             with open(OFFLINE_QUEUE_FILE, "r") as f:
                 return json.load(f)
        return []

    def _save_queue(self):
        with open(OFFLINE_QUEUE_FILE, "w") as f:
            json.dump(self.offline_queue, f)

    def _sync_worker(self):
        while True:
            if self.offline_queue:
                print(f"[*] Attempting to sync {len(self.offline_queue)} offline logs...")
                try:
                    resp = self.session.post(
                        f"{BASE_URL}/attendance/sync",
                        json={"logs": self.offline_queue}
                    )
                    if resp.status_code == 200:
                        print(f"[+] Synced {len(self.offline_queue)} logs.")
                        self.offline_queue = []
                        self._save_queue()
                except Exception as e:
                    print(f"[-] Sync failed: {e}")
            time.sleep(30) # Retry every 30 seconds

    def authenticate(self):
        print("[*] Authenticating with backend...")
        try:
            resp = self.session.post(f"{BASE_URL}/auth/login/access-token", data={
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD
            })
            if resp.status_code == 200:
                self.token = resp.json()["access_token"]
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                print("[+] Authentication successful.")
            else:
                print(f"[-] Authentication failed: {resp.text}")
        except Exception as e:
            print(f"[-] Connection error: {e}")

    def check_in(self, embedding, is_live=0):
        log_data = {
            "face_embedding": embedding.tolist(),
            "source": "edge",
            "is_live": is_live,
            "timestamp": datetime.utcnow().isoformat()
        }

        
        try:
            resp = self.session.post(
                f"{BASE_URL}/attendance/check-in",
                json=log_data,
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json()
                print(f"[LOG] Attendance Recorded: User {data['user_id']} at {data['check_in']}")
                return data
            else:
                print(f"[-] Server error ({resp.status_code}), queueing locally...")
                self.offline_queue.append(log_data)
                self._save_queue()
                return None
        except Exception as e:
            print(f"[-] Connection lost, queueing locally...")
            self.offline_queue.append(log_data)
            self._save_queue()
            return None

    def enroll(self, user_id, embedding):
        try:
            resp = self.session.post(
                f"{BASE_URL}/users/{user_id}/enroll",
                json={"face_embedding": embedding.tolist()}
            )
            if resp.status_code == 200:
                print(f"[+] User {user_id} enrolled successfully.")
                return True
            else:
                print(f"[-] Enrollment failed: {resp.text}")
                return False
        except Exception as e:
            print(f"[-] Request error: {e}")
            return False

def main():
    client = AttendanceClient()
    video_capture = cv2.VideoCapture(0)

    print("\n--- AI Edge Attendance Client with Liveness ---")
    print("Commands: [r] Register | [q] Quit")

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Liveness detection via landmarks
        face_landmarks_list = face_recognition.face_landmarks(rgb_small_frame)
        for face_landmarks in face_landmarks_list:
            left_eye = face_landmarks['left_eye']
            right_eye = face_landmarks['right_eye']
            ear = (eye_aspect_ratio(left_eye) + eye_aspect_ratio(right_eye)) / 2.0
            
            if ear < EYE_AR_THRESH:
                client.blink_counter += 1
            else:
                if client.blink_counter >= EYE_AR_CONSEC_FRAMES:
                    client.blink_count += 1
                    print(f"[*] Blink detected! Total count: {client.blink_count}")
                client.blink_counter = 0

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            top *= 4; right *= 4; bottom *= 4; left *= 4
            
            # Identify via Backend with Liveness data
            is_live = 1 if client.blink_count > 0 else 0
            res = client.check_in(face_encoding, is_live=is_live)

            
            name = "Recognized" if res else "Unknown"
            color = (0, 255, 0) if res else (0, 0, 255)

            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

        cv2.imshow('Attendance System', frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('r'):
            if len(face_encodings) == 1:
                u_id = input("Enter User ID for enrollment: ")
                client.enroll(u_id, face_encodings[0])
            else:
                print("Error: Ensure exactly one face is visible.")

        elif key == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
