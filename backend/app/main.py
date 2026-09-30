import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.routers.analyze import router as analyze_router


def _warm_up_model():
    try:
        from app.services.prediction_service import get_model
        get_model()
        print("Model loaded and ready.")
    except Exception as exc:
        print("Model warm-up skipped:", exc)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Load the model in the background so the first request isn't slow.
    threading.Thread(target=_warm_up_model, daemon=True).start()
    yield


app = FastAPI(
    title="Fake Image Detector API",
    description="Detect AI-generated images from website URLs or uploaded files",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router)


@app.get("/")
def home():
    return {"status": "success", "message": "Fake Image Detector Backend is Running 🚀"}


@app.get("/health")
def health():
    try:
        from app.services.prediction_service import is_model_ready
        model_ready = is_model_ready()
    except Exception:
        model_ready = False
    return {"status": "healthy", "model_ready": model_ready}
