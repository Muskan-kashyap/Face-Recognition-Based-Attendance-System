"""Biometrics Microservice — FastAPI entry point."""
from fastapi import FastAPI
from app.routers.biometrics import router as bio_router

app = FastAPI(
    title="Biometrics & AI Engine",
    version="1.0.0",
    description="Face enrollment, HNSW similarity search, liveness, and emotion analysis",
)

app.include_router(bio_router)


@app.get("/health")
def health():
    return {"status": "biometrics service operational"}
