import os
import time
import logging
import httpx
from typing import Dict
from fastapi import FastAPI, Request, Response, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from starlette.background import BackgroundTask

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Gateway")

app = FastAPI(
    title="Core API Gateway",
    version="1.0.0",
    description="Unified API Gateway proxying multi-tenant requests to backend microservices"
)

# CORS configuration
ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "http://127.0.0.1:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Microservice routing configuration
SERVICES: Dict[str, str] = {
    "auth": os.getenv("AUTH_SVC_URL", "http://127.0.0.1:8001"),
    "biometrics": os.getenv("BIO_SVC_URL", "http://127.0.0.1:8002"),
    "attendance": os.getenv("ATT_SVC_URL", "http://127.0.0.1:8003"),
    "analytics": os.getenv("ANAL_SVC_URL", "http://127.0.0.1:8004"),
}

# HTTPX Async Client for proxying
client = httpx.AsyncClient(timeout=60.0)

# Simplistic Token Bucket Rate Limiter
RATE_LIMIT_STRICT = 100 # requests per minute
request_counts: Dict[str, list] = {}

def check_rate_limit(client_ip: str):
    current_time = time.time()
    # clean old requests
    request_counts[client_ip] = [t for t in request_counts.get(client_ip, []) if current_time - t < 60]
    
    if len(request_counts[client_ip]) >= RATE_LIMIT_STRICT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 100 requests per minute."
        )
    request_counts[client_ip].append(current_time)

@app.middleware("http")
async def gateway_middleware(request: Request, call_next):
    # Enforce basic security headers
    client_ip = request.client.host if request.client else "unknown"
    try:
        check_rate_limit(client_ip)
    except HTTPException as exc:
        return Response(content=exc.detail, status_code=exc.status_code)
    
    start_time = time.time()
    response = await call_next(request)
    duration = (time.time() - start_time) * 1000
    
    response.headers["X-Gateway-Process-Time-Ms"] = f"{duration:.2f}"
    return response

async def proxy_request(service_name: str, path: str, request: Request) -> Response:
    """
    Proxies requests from the gateway to the appropriate downstream microservice.
    """
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail="Service not found")

    target_url = f"{SERVICES[service_name]}{path}"
    
    # Extract query params and body
    query_params = dict(request.query_params)
    body = await request.body()
    
    # Copy request headers (omitting Host header to prevent loops)
    headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
    
    # Perform proxy request
    try:
        response = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            params=query_params,
            content=body,
        )
    except httpx.RequestError as exc:
        logger.error(f"Proxy request to {service_name} failed: {exc}")
        return Response(
            content="Service temporarily unavailable",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    # Return target microservice response
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers)
    )

# Auth Microservice Route Matches
@app.api_route("/api/v1/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def route_auth(path: str, request: Request):
    return await proxy_request("auth", f"/api/v1/auth/{path}", request)

# Biometrics Microservice Route Matches
@app.api_route("/api/v1/biometrics/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_biometrics(path: str, request: Request):
    return await proxy_request("biometrics", f"/api/v1/biometrics/{path}", request)

# Attendance Microservice Route Matches
@app.api_route("/api/v1/attendance/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_attendance(path: str, request: Request):
    return await proxy_request("attendance", f"/api/v1/attendance/{path}", request)

# Analytics Microservice Route Matches
@app.api_route("/api/v1/analytics/{path:path}", methods=["GET"])
async def route_analytics(path: str, request: Request):
    return await proxy_request("analytics", f"/api/v1/analytics/{path}", request)

@app.get("/health")
def health_check():
    return {"status": "gateway operational"}
