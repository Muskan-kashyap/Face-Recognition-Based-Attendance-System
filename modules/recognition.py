import cv2
from deepface import DeepFace
import pickle
import os

def load_embeddings():
    """
    Load saved facial embeddings from pickle file.
    """
    embeddings_file = 'embeddings.pkl'
    if os.path.exists(embeddings_file):
        with open(embeddings_file, 'rb') as f:
            return pickle.load(f)
    else:
        print("No registered users found. Please run registration first.")
        return {}

def recognize_faces():
    """
    Continuous live recognition pipeline.
    Detects faces in live feed, extracts embeddings, and compares against saved vectors.
    """
    embeddings = load_embeddings()
    if not embeddings:
        return

    # Initialize webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        return

    print("Starting live recognition. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame")
            break

        try:
            # Extract faces with locations
            faces = DeepFace.extract_faces(frame, detector_backend='opencv', enforce_detection=False)
            if faces:
                for face_data in faces:
                    facial_area = face_data['facial_area']
                    x, y, w, h = facial_area['x'], facial_area['y'], facial_area['w'], facial_area['h']

                    # Extract embedding for the face
                    face_img = face_data['face']  # This is the cropped face
                    # But DeepFace.represent can take the full frame, but to be precise, use the cropped
                    # Actually, for consistency, use represent on the cropped face
                    embedding_result = DeepFace.represent(face_img, model_name='Facenet', enforce_detection=False)
                    if embedding_result:
                        live_embedding = embedding_result[0]['embedding']

                        # Compare against all saved embeddings
                        min_dist = float('inf')
                        best_match = None
                        for name, saved_emb in embeddings.items():
                            # Compute distance using DeepFace verify
                            verification = DeepFace.verify(saved_emb, live_embedding, model_name='Facenet', enforce_detection=False, distance_metric='cosine')
                            dist = verification['distance']
                            if dist < min_dist:
                                min_dist = dist
                                best_match = name

                        # Check threshold
                        if min_dist < 0.4:
                            label = best_match
                            color = (0, 255, 0)  # Green for recognized
                        else:
                            label = "Unknown"
                            color = (0, 0, 255)  # Red for unknown

                        # Draw rectangle and label
                        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        except Exception as e:
            print(f"Error in recognition: {e}")

        cv2.imshow('Live Recognition', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    recognize_faces()