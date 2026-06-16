import logging
import base64
import requests
from typing import Tuple

logger = logging.getLogger(__name__)

AI_SERVICE_URL = "http://ai-service:8002/api/v1/biometrics"

class LivenessService:
    @staticmethod
    def detect_liveness(image_bytes: bytes) -> Tuple[bool, float]:
        """
        Proxy method to ai-service for liveness detection.
        """
        try:
            b64_img = base64.b64encode(image_bytes).decode('utf-8')
            resp = requests.post(f"{AI_SERVICE_URL}/liveness", json={"image_base64": b64_img}, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("is_live", False), data.get("confidence", 0.0)
            return False, 0.0
        except Exception as e:
            logger.error("Error communicating with AI service for liveness: %s", e)
            return False, 0.0

liveness_service = LivenessService()



