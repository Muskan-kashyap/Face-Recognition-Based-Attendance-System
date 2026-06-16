from fastapi import APIRouter
from app.routers import auth, users, attendance, org, ticketing, payroll, reimbursement, admin

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(attendance.router, prefix="/attendance", tags=["attendance"])
api_router.include_router(org.router, prefix="/org", tags=["organization"])
api_router.include_router(ticketing.router, prefix="/ticketing", tags=["ticketing"])
api_router.include_router(payroll.router, prefix="/payroll", tags=["payroll"])
api_router.include_router(reimbursement.router, prefix="/reimbursement", tags=["reimbursement"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
