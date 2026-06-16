"""JWT dependency guards reused by downstream services (Biometrics, Attendance, etc.)."""
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from typing import List

JWT_SECRET = os.getenv("JWT_SECRET", "SuperSecretKeyAtLeast32CharsLongMustBeComplex!")
JWT_ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user_claims(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        return payload
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token validation failed: {exc}")


class PermissionGuard:
    def __init__(self, required: List[str]):
        self.required = required

    def __call__(self, claims: dict = Depends(get_current_user_claims)) -> dict:
        user_perms = claims.get("permissions", [])
        for perm in self.required:
            if perm not in user_perms:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Missing scope: {perm}")
        return claims


class TenantGuard:
    def __call__(self, claims: dict = Depends(get_current_user_claims)) -> str:
        org_id = claims.get("org_id")
        if not org_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing tenant scope in token")
        return org_id
