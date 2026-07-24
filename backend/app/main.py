from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.analyze import router as analyze_router





app = FastAPI(
    title="Fake Image Detector API",
    description="Detect AI-generated images from website URLs",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router)


@app.get("/")
def home():
    return {
        "status": "success",
        "message": "Fake Image Detector Backend is Running 🚀"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }