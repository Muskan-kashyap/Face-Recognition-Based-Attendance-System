import logging
import numpy as np
from typing import List, Optional

logger = logging.getLogger(__name__)

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False


class FaceEngine:
    @staticmethod
    def get_embedding(image_bytes: bytes) -> Optional[List[float]]:
        """
        Given a raw image bytes array, return a 128-d face embedding.
        If no face or multiple faces are detected, return None.
        """
        if not FACE_RECOGNITION_AVAILABLE:
            raise RuntimeError(
                "face_recognition module not available. Biometric service offline."
            )

        import io
        from PIL import Image

        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            image_array = np.array(image)
        except Exception as e:
            logger.error("Error loading image: %s", e)
            return None

        face_locations = face_recognition.face_locations(image_array)
        if len(face_locations) != 1:
            return None

        face_encodings = face_recognition.face_encodings(
            image_array, face_locations
        )
        if len(face_encodings) == 0:
            return None

        return face_encodings[0].tolist()

    @staticmethod
    def compare_embeddings(
        embedding1: List[float],
        embedding2: List[float],
        tolerance: float = 0.5,
    ) -> bool:
        """Compare two 128-d face embeddings and return True if they match."""
        enc1 = np.array(embedding1)
        enc2 = np.array(embedding2)
        distance = np.linalg.norm(enc1 - enc2)
        return distance <= tolerance

    @staticmethod
    def get_emotion(image_bytes: bytes) -> str:
        """Analyze the face in the image for emotional expression."""
        try:
            from deepface import DeepFace
            import io
            from PIL import Image

            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            image_array = np.array(image)

            objs = DeepFace.analyze(
                img_path=image_array,
                actions=["emotion"],
                enforce_detection=False,
            )

            if objs:
                return objs[0]["dominant_emotion"]
            return "neutral"
        except Exception as e:
            logger.error("Emotion analysis failed: %s", e)
            return "neutral"


face_engine = FaceEngine()


