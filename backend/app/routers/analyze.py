import os

from fastapi import APIRouter, HTTPException
from app.schemas.schema import WebsiteRequest
from app.utils.helper import is_public_url
from app.services.image_service import check_website
from app.scraper.scraper import scrape_images

router = APIRouter(
    prefix="/analyze",
    tags=["Website Analysis"]
)

@router.post("/")
def analyze(request: WebsiteRequest):

    url = request.url

    # Validate URL
    if not is_public_url(url):
        return {
            "status": "error",
            "message": "Enter a publicly reachable HTTP(S) URL."
        }

    # Check website
    reachable, status = check_website(url)

    if not reachable:
        return {
            "status": "error",
            "message": "Website is not reachable.",
            "status_code": status
        }

    # Scrape images
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

    if predictions:
        for image, prediction in zip(images, predictions):
            image["prediction"] = prediction.get("prediction")
            image["confidence"] = prediction.get("confidence")

    # The temporary path is an implementation detail and must not be exposed
    # to API clients.
    for image in images:
        image.pop("saved_path", None)

    return {
        "status": "success",
        "message": "Images scraped successfully.",
        "website": url,
        "status_code": status,
        "total_images": len(images),
        "images": images
    }
