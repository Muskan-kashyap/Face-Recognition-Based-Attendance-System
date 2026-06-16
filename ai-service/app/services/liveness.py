import logging
import io
import numpy as np
from typing import Tuple

logger = logging.getLogger(__name__)

class LivenessService:
    @staticmethod
    def detect_liveness(image_bytes: bytes) -> Tuple[bool, float]:
        """
        Detects if the face in the image is a real person or a spoof (photo/video).
        Returns (is_live, confidence_score).

        Uses DeepFace's MiniFASNet anti-spoofing model for production-grade
        liveness detection.
        """
        try:
            from PIL import Image
            from deepface import DeepFace

            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            image_array = np.array(image)

            # Enforce detection ensures we don't proceed if there is no face.
            # Anti-spoofing uses MiniFASNet to detect 2D presentation attacks.
            faces = DeepFace.extract_faces(
                img_path=image_array,
                anti_spoofing=True,
                enforce_detection=True
            )

            if len(faces) == 0:
                return False, 0.0

            # Check the first detected face
            face_info = faces[0]
            is_live = face_info.get("is_real", False)
            confidence = face_info.get("antispoof_score", 0.0)

            return bool(is_live), float(confidence)

        except ValueError as e:
            # DeepFace raises ValueError if no face is detected when enforce_detection=True
            logger.warning("Liveness detection: No face detected. %s", e)
            return False, 0.0
        except Exception as e:
            logger.error("Liveness detection error: %s", e)
            return False, 0.0

liveness_service = LivenessService()


