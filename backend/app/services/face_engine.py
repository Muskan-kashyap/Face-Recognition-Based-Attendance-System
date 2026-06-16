import logging
import base64
import requests
from typing import List, Optional

logger = logging.getLogger(__name__)

# URL of the AI microservice
AI_SERVICE_URL = "http://ai-service:8002/api/v1/biometrics"

class FaceEngine:
    """
    HTTP Client proxy for the Biometrics Microservice (ai-service).
    Offloads heavy ML operations (DeepFace, PyTorch) to the dedicated service.
    """

    @staticmethod
    def get_embedding(image_bytes: bytes) -> Optional[List[float]]:
        try:
            b64_img = base64.b64encode(image_bytes).decode('utf-8')
            resp = requests.post(f"{AI_SERVICE_URL}/extract", json={"image_base64": b64_img}, timeout=5)
            if resp.status_code == 200:
                return resp.json().get("embedding")
            return None
        except Exception as e:
            logger.error("Error communicating with AI service for embedding: %s", e)
            return None

    @staticmethod
    def get_emotion(image_bytes: bytes) -> str:
        try:
            b64_img = base64.b64encode(image_bytes).decode('utf-8')
            resp = requests.post(f"{AI_SERVICE_URL}/emotion", json={"image_base64": b64_img}, timeout=5)
            if resp.status_code == 200:
                return resp.json().get("emotion", "neutral")
            return "neutral"
        except Exception as e:
            logger.error("Error communicating with AI service for emotion: %s", e)
            return "neutral"

face_engine = FaceEngine()

