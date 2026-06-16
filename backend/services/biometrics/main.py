import base64
import logging
import cv2
import numpy as np
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BiometricsService")

app = FastAPI(title="Biometrics Service", version="1.0.0")

# Database configuration
DATABASE_URL = "postgresql://postgres:postgrespassword@postgres:5432/face_attendance_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Request schemas
class EnrollRequest(BaseModel):
    enrollment_token: str
    image_base64: str

class VerifyRequest(BaseModel):
    image_base64: str
    org_id: str

# Liveness detector helper
def check_liveness(image_bytes: bytes) -> tuple[bool, float]:
    """
    Computes Laplacian variance to detect flat-image spoofs (e.g. tablet displays).
    """
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return False, 0.0
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        variance = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        is_live = variance > 100.0
        confidence = min(variance / 500.0, 1.0)
        return is_live, confidence
    except Exception as e:
        logger.error(f"Liveness evaluation failed: {e}")
        return False, 0.0

# Extract embedding helper (simulation fallback matching FaceEngine interface)
def extract_embedding(image_bytes: bytes) -> Optional[List[float]]:
    # Mocking standard normalized 128-d vector extraction for scaffolding
    # In a full run, this invokes face_recognition.face_encodings() or ArcFace.
    vec = np.random.randn(128)
    return (vec / np.linalg.norm(vec)).tolist()

@app.post("/api/v1/biometrics/enroll")
def enroll_face(req: EnrollRequest, db: Session = Depends(get_db)):
    try:
        image_bytes = base64.b64decode(req.image_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 payload")
    
    # 1. Enforce Liveness during Onboarding
    is_live, score = check_liveness(image_bytes)
    if not is_live:
        raise HTTPException(status_code=400, detail=f"Biometric onboarding failed: Liveness rejected (Score: {score:.2f})")
    
    # 2. Extract biometric details
    embedding = extract_embedding(image_bytes)
    if not embedding:
        raise HTTPException(status_code=400, detail="No faces detected in the provided image")
    
    # 3. Simulate user fetch and database mapping from token
    # In microservices, we request verification from the Auth Service first.
    user_query = db.execute(
        text("SELECT id, org_id FROM users WHERE enrollment_token = :token AND is_deleted = 0"),
        {"token": req.enrollment_token}
    ).fetchone()
    
    if not user_query:
        raise HTTPException(status_code=404, detail="Enrollment token is invalid or expired")
    
    user_id, org_id = user_query
    
    # Generate mock Schnorr commitment
    schnorr_commitment = f"schnorr_P_xG_{req.enrollment_token[:16]}"
    
    # Store embedding
    db.execute(
        text(
            "INSERT INTO face_embeddings (user_id, embedding, zkp_public_commitment, model_name, is_active) "
            "VALUES (:user_id, :embedding, :zkp, 'ArcFace', 1)"
        ),
        {"user_id": user_id, "embedding": embedding, "zkp": schnorr_commitment}
    )
    
    # Mark token used
    db.execute(
        text("UPDATE users SET enrollment_token = NULL WHERE id = :user_id"),
        {"user_id": user_id}
    )
    db.commit()
    return {"status": "success", "detail": "Face embedding enrolled successfully"}

@app.post("/api/v1/attendance/verify")
def verify_attendance(req: VerifyRequest, db: Session = Depends(get_db)):
    try:
        image_bytes = base64.b64decode(req.image_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 payload")
    
    # 1. Execute Liveness verification
    is_live, score = check_liveness(image_bytes)
    if not is_live:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Liveness check failed. Access denied.")
    
    # 2. Extract embedding
    embedding = extract_embedding(image_bytes)
    if not embedding:
        raise HTTPException(status_code=400, detail="No face detected in camera feed")
    
    # 3. Query pgvector HNSW database partition using cosine distance operator <=>
    # Returns closest match inside tenant boundary under the distance threshold (e.g. 0.45)
    query = text(
        "SELECT f.user_id, u.full_name, (f.embedding <=> :embedding) as distance "
        "FROM face_embeddings f "
        "JOIN users u ON f.user_id = u.id "
        "WHERE u.org_id = :org_id AND f.is_active = 1 AND u.is_deleted = 0 "
        "ORDER BY f.embedding <=> :embedding LIMIT 1"
    )
    
    match = db.execute(
        query, 
        {"embedding": str(embedding), "org_id": req.org_id}
    ).fetchone()
    
    if not match or match.distance > 0.45:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=f"Verification failed: User unrecognized. Distance: {match.distance if match else 1.0:.3f}"
        )
        
    return {
        "status": "verified",
        "user_id": match.user_id,
        "full_name": match.full_name,
        "distance": float(match.distance),
        "is_live": True,
        "emotion": "happy" # Dominant expression mock
    }
