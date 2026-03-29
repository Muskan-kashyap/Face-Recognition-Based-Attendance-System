from fastapi import APIRouter
auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/login")
async def login():
    return {"message": "Login successful"}

@auth_router.post("/register")
async def register():
    return {"message": "Registration successful"}

@auth_router.post("/logout")
async def logout():
    return {"message": "Logout successful"}

@auth_router.post("/refresh")
async def refresh():
    return {"message": "Token refreshed successfully"}