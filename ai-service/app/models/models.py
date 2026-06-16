from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, CheckConstraint, text
from pgvector.sqlalchemy import Vector
from app.db.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class FaceEmbedding(Base):
    __tablename__ = 'face_embeddings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True) # References users.id in Auth Service
    embedding = Column(Vector(128), nullable=False)        # 128-d FaceNet or ArcFace embedding
    zkp_public_commitment = Column(String(512), nullable=True) # Schnorr signature public key
    model_name = Column(String(50), nullable=False, default='ArcFace')
    is_active = Column(Integer, nullable=False, default=1) # 1=current, 0=superseded
    enrolled_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    __table_args__ = (
        CheckConstraint('is_active IN (0, 1)', name='ck_face_embed_is_active'),
        Index('ix_face_embeddings_active_user', 'user_id', postgresql_where=text("is_active = 1"))
    )

    def __repr__(self):
        return f"<FaceEmbedding id={self.id} user={self.user_id} active={self.is_active}>"
