from fastapi import APIRouter
from app.schemas.schema import WebsiteRequest
from app.utils.helper import is_valid_url
from app.services.image_service import check_website
from app.services.prediction_service import predict_images
from app.scraper.scraper import scrape_images

router = APIRouter(
    prefix="/analyze",
    tags=["Website Analysis"]
)

@router.post("/")
def analyze(request: WebsiteRequest):

    url = request.url

    # Validate URL
    if not is_valid_url(url):
        return {
            "status": "error",
            "message": "Invalid URL format."
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
    predictions = predict_images(image_paths)

    if predictions is not None:
        for image, prediction in zip(images, predictions):
            image["prediction"] = prediction.get("prediction")
            image["confidence"] = prediction.get("confidence")
    else:
        for image in images:
            image["prediction"] = None
            image["confidence"] = None

    return {
        "status": "success",
        "message": "Images scraped successfully.",
        "website": url,
        "status_code": status,
        "total_images": len(images),
        "images": images
    }