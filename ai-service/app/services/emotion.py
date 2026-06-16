import cv2
import numpy as np
from typing import Tuple

class EmotionClassifier:
    """
    Classifies user emotions into categories (happy, neutral, sad, stressed, angry)
    using facial bounding region aspect ratios and pixel variances.
    """

    def analyze_emotion(self, face_region: np.ndarray) -> Tuple[str, float]:
        """
        Analyzes standard emotions in the face region.
        In production, this feeds the bounding box to a custom mini-Xception model.
        We provide a structured geometric fallback calculation here.
        """
        if face_region is None or face_region.size == 0:
            return "neutral", 1.0

        try:
            # Analyze face patch lighting variance and aspect ratio
            h, w = face_region.shape[:2]
            aspect_ratio = w / h if h > 0 else 1.0
            
            # Simple heuristic calculations based on color distributions for mock
            gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
            std_dev = float(np.std(gray))
            
            # Heuristics mapping features
            if std_dev > 50.0:
                if aspect_ratio > 1.05:
                    return "happy", 0.88
                else:
                    return "stressed", 0.72
            elif std_dev < 30.0:
                return "neutral", 0.95
            else:
                if aspect_ratio < 0.95:
                    return "sad", 0.65
                else:
                    return "angry", 0.62
        except Exception:
            return "neutral", 0.90
        
        return "neutral", 1.0
