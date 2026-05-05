
from sqlalchemy.orm import Session
from app.db.models.all_models import User
from app.core.security import get_password_hash
from app.schema.password_reset import ForgotPasswordRequest
from typing import Optional
import secrets
from datetime import datetime, timedelta

class CRUDPassword:
    @staticmethod
    def send_reset_email(db: Session, email: str) -> bool:
        """Generate reset token and save to user record. Email sent by caller."""
        user = db.query(User).filter(User.email == email, User.is_deleted == 0).first()
        if not user:
            return False
        
        # Generate secure 32-byte token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        # Save to user record
        user.reset_token = token
        user.reset_token_expires = expires_at
        
        db.commit()
        return True
    
    @staticmethod
    def verify_reset_token(db: Session, token: str) -> Optional[int]:
        """Verify reset token and return user_id if valid."""
        user = db.query(User).filter(
            User.reset_token == token,
            User.reset_token_expires > datetime.utcnow(),
            User.is_deleted == 0
        ).first()
        if not user:
            return None
        return user.id
    
    @staticmethod
    def reset_password(db: Session, user_id: int, new_password: str):
        """Complete password reset."""
        user = db.query(User).filter(User.id == user_id, User.is_deleted == 0).first()
        if not user:
            raise ValueError("User not found")
        
        user.hashed_password = get_password_hash(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        
        db.commit()
        return True

password_crud = CRUDPassword()

