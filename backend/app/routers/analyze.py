import io
import os
import threading
import time
from collections import OrderedDict

from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from app.schemas.schema import WebsiteRequest
from app.scraper.scraper import scrape_images
from app.services.image_service import check_website
from app.utils.helper import is_public_url

router = APIRouter(prefix="/analyze", tags=["Website Analysis"])

CACHE_TTL_SECONDS = int(os.environ.get("CACHE_TTL_SECONDS", "600"))
CACHE_MAX_ITEMS = 50
MAX_UPLOAD_BYTES = int(os.environ.get("MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))

_cache: "OrderedDict[str, tuple[float, dict]]" = OrderedDict()
_cache_lock = threading.Lock()


def _cache_get(key: str):
    with _cache_lock:
        item = _cache.get(key)
        if not item:
            return None
        if time.time() - item[0] > CACHE_TTL_SECONDS:
            _cache.pop(key, None)
            return None
        _cache.move_to_end(key)
        return item[1]


def _cache_set(key: str, value: dict):
    with _cache_lock:
        _cache[key] = (time.time(), value)
        _cache.move_to_end(key)
        while len(_cache) > CACHE_MAX_ITEMS:
            _cache.popitem(last=False)


def build_summary(images: list[dict]) -> dict:
    counts = {"AI": 0, "REAL": 0, "UNCERTAIN": 0, "UNKNOWN": 0}
    for image in images:
        label = image.get("prediction") or "UNKNOWN"
        counts[label if label in counts else "UNKNOWN"] += 1

    analyzed = counts["AI"] + counts["REAL"] + counts["UNCERTAIN"]
    ai_percentage = round(counts["AI"] / analyzed * 100, 1) if analyzed else 0.0

    if analyzed == 0:
        verdict = "No images could be analyzed"
    elif ai_percentage >= 60:
        verdict = "Mostly AI-generated"
    elif ai_percentage >= 25:
        verdict = "Mixed: AI-generated and real"
    else:
        verdict = "Mostly real images"

    return {
        "ai_count": counts["AI"],
        "real_count": counts["REAL"],
        "uncertain_count": counts["UNCERTAIN"],
        "unknown_count": counts["UNKNOWN"],
        "ai_percentage": ai_percentage,
        "verdict": verdict,
    }


@router.post("/")
def analyze(request: WebsiteRequest):
    started = time.time()
    url = request.url

    if not is_public_url(url):
        raise HTTPException(status_code=400, detail="Enter a publicly reachable HTTP(S) URL.")

    cached = _cache_get(url)
    if cached:
        return {**cached, "cached": True}

    reachable, status = check_website(url)
    if not reachable:
        raise HTTPException(
            status_code=502,
            detail=f"Website is not reachable (status: {status if status else 'no response'}).",
        )

    images = scrape_images(url)
    image_paths = [image["saved_path"] for image in images]

    predictions = []
    if image_paths:
        try:
            from app.services.prediction_service import predict_images
            predictions = predict_images(image_paths)
        except Exception as exc:
            raise HTTPException(status_code=503, detail="Prediction service is unavailable.") from exc
        finally:
            for image_path in image_paths:
                try:
                    os.remove(image_path)
                except OSError:
                    pass

    for image, prediction in zip(images, predictions):
        image.update({k: v for k, v in prediction.items()})

    # The temporary path is an implementation detail; never expose it.
    for image in images:
        image.pop("saved_path", None)

    response = {
        "status": "success",
        "message": "Images analyzed successfully." if images else "No usable images found on this page.",
        "website": url,
        "status_code": status,
        "total_images": len(images),
        "summary": build_summary(images),
        "images": images,
        "elapsed_seconds": round(time.time() - started, 2),
        "cached": False,
    }
    if images:
        _cache_set(url, response)
    return response


@router.post("/upload")
async def analyze_upload(file: UploadFile = File(...)):
    """Classify a single uploaded image and return a Grad-CAM heat-map."""
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Image is too large (max 10 MB).")

    try:
        image = Image.open(io.BytesIO(data))
        image.load()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(status_code=400, detail="File is not a valid image.")

    try:
        from app.services.prediction_service import explain_image, predict_pil

        result = predict_pil(image)
        try:
            heatmap = explain_image(image)
        except Exception:
            heatmap = None
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Prediction service is unavailable.") from exc

    item = {
        "filename": file.filename or "uploaded_image",
        "width": image.width,
        "height": image.height,
        "heatmap": heatmap,
        **result,
    }
    return {
        "status": "success",
        "message": "Image analyzed successfully.",
        "total_images": 1,
        "summary": build_summary([item]),
        "images": [item],
    }
