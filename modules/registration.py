# import cv2
# from deepface import DeepFace
# import pickle
# import os

# def register_face(name):
#     """
#     Registers a face by capturing from webcam, extracting facial embedding using Facenet,
#     and saving to a pickle file.
#     """
#     # Initialize webcam
#     cap = cv2.VideoCapture(0)
#     if not cap.isOpened():
#         print("Cannot open camera")
#         return False

#     print("Press 'c' to capture face, 'q' to quit")

#     captured = False
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             print("Failed to capture frame")
#             break

#         cv2.imshow('Registration', frame)
#         key = cv2.waitKey(1) & 0xFF

#         if key == ord('c'):
#             # Detect and extract embedding
#             try:
#                 result = DeepFace.represent(frame, model_name='Facenet', enforce_detection=True)
#                 if result:
#                     embedding = result[0]['embedding']
#                     # Load existing embeddings if file exists
#                     embeddings_file = 'embeddings.pkl'
#                     if os.path.exists(embeddings_file):
#                         with open(embeddings_file, 'rb') as f:
#                             embeddings = pickle.load(f)
#                     else:
#                         embeddings = {}

#                     # Add new embedding
#                     embeddings[name] = embedding

#                     # Save back
#                     with open(embeddings_file, 'wb') as f:
#                         pickle.dump(embeddings, f)

#                     print(f"Face registered for {name}")
#                     captured = True
#                     break
#                 else:
#                     print("No face detected, try again")
#             except Exception as e:
#                 print(f"Error extracting features: {e}")
#         elif key == ord('q'):
#             break

#     cap.release()
#     cv2.destroyAllWindows()
#     return captured

# if __name__ == "__main__":
#     name = input("Enter name for registration: ")
#     register_face(name)

# import cv2
# import face_recognition
# import numpy as np
# from datetime import datetime

# # 1. DATABASE MODULE (Simplified)
# # In a real app, these would be loaded from a SQL database or Folder
# known_face_encodings = []
# known_face_names = []

# def load_employee_data():
#     # Load a sample picture and learn how to recognize it.
#     image = face_recognition.load_image_file("employee_1.jpg")
#     encoding = face_recognition.face_encodings(image)[0]
#     known_face_encodings.append(encoding)
#     known_face_names.append("John Doe")

# # 2. LOGGING MODULE
# def log_attendance(name):
#     with open("attendance.csv", "a") as f:
#         now = datetime.now()
#         dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
#         f.writelines(f"\n{name}, {dt_string}")

# # MAIN EXECUTION
# load_employee_data()
# video_capture = cv2.VideoCapture(0)

# while True:
#     # Capture frame-by-frame
#     ret, frame = video_capture.read()

#     # 3. PRE-PROCESSING & ALIGNMENT
#     # Resize frame to 1/4 size for faster face recognition processing
#     small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
#     rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

#     # 4. FEATURE EXTRACTION (Finding faces and their 128-d embeddings)
#     face_locations = face_recognition.face_locations(rgb_small_frame)
#     face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

#     # 5. MATCHING MODULE
#     for face_encoding in face_encodings:
#         # Compare face with the database
#         matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
#         name = "Unknown"

#         # Calculate the Euclidean distance (the smaller the distance, the better the match)
#         face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
#         best_match_index = np.argmin(face_distances)
        
#         if matches[best_match_index]:
#             name = known_face_names[best_match_index]
#             # 6. LOGGING
#             log_attendance(name)

#     # Display results on the screen (Optional UI)
#     cv2.imshow('Attendance System', frame)

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# video_capture.release()
# cv2.destroyAllWindows()

import cv2
import face_recognition
import numpy as np
import os
import sys
from datetime import datetime

# --- 0. PRE-FLIGHT CHECK ---
try:
    import face_recognition_models
except ImportError:
    print("\n[!] Error: face_recognition_models not found.")
    print("Run: uv add 'face_recognition_models @ git+https://github.com/ageitgey/face_recognition_models'")
    sys.exit(1)

# --- 1. DATABASE & PERSISTENCE ---
known_face_encodings = []
known_face_names = []
already_logged = set()

def save_new_user(name, encoding, image_frame):
    known_face_encodings.append(encoding)
    known_face_names.append(name)
    
    if not os.path.exists("registered_users"):
        os.makedirs("registered_users")
    cv2.imwrite(f"registered_users/{name}.jpg", image_frame)
    print(f"---> User '{name}' registered and active!")

# --- 2. LOGGING MODULE ---
def log_attendance(name):
    if name not in already_logged and name != "Unknown":
        with open("attendance.csv", "a") as f:
            now = datetime.now()
            f.write(f"{name}, {now.strftime('%Y-%m-%d')}, {now.strftime('%H:%M:%S')}\n")
        already_logged.add(name)
        print(f"[LOG] Attendance recorded: {name}")

# --- MAIN EXECUTION ---
video_capture = cv2.VideoCapture(0)

print("\n--- Attendance System Initialized ---")
print("Commands: [r] Register | [q] Quit")

while True:
    ret, frame = video_capture.read()
    if not ret:
        break

    # 3. PRE-PROCESSING (1/4 size for speed)
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # 4. DETECTION & EXTRACTION
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    # 5. MATCHING & UI
    # We zip locations and encodings to handle multiple faces correctly
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        
        # Scale back up for the UI
        top *= 4; right *= 4; bottom *= 4; left *= 4
        
        name = "Unknown"
        color = (0, 0, 255) # Red for Unknown

        if known_face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                    color = (0, 255, 0) # Green for Recognized
                    log_attendance(name)

        # Draw UI
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
        cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

    cv2.imshow('Attendance System', frame)
    key = cv2.waitKey(1) & 0xFF

    # 6. REGISTRATION TRIGGER
    if key == ord('r'):
        if len(face_encodings) == 1:
            # We use the raw frame for higher quality saving
            new_name = input("Enter name for registration: ")
            save_new_user(new_name, face_encodings[0], frame)
        else:
            print("Error: Ensure exactly one face is visible to register.")

    elif key == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()