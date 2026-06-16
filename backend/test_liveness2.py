from deepface import DeepFace
import numpy as np
import cv2
import json

# create a dummy image (e.g., all 255s)
img = np.full((300, 300, 3), 255, dtype=np.uint8)

try:
    res = DeepFace.extract_faces(img_path=img, anti_spoofing=True, enforce_detection=False)
    # The output is a list of dictionaries.
    # We want to see what keys are returned.
    print(res[0].keys())
    print("antispoof_score:", res[0].get("antispoof_score"))
except Exception as e:
    print("Error:", e)
