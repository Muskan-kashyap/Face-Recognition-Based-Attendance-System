from deepface import DeepFace
import numpy as np
import cv2

# create dummy image
img = np.zeros((300, 300, 3), dtype=np.uint8)

try:
    res = DeepFace.extract_faces(img_path=img, anti_spoofing=True, enforce_detection=False)
    print("Anti-spoofing returned:", res[0].get("is_real"))
except Exception as e:
    print("Error:", e)
