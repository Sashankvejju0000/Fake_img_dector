import os
import sys

try:
    import torch
    import torch.nn as nn
    from torchvision import models
except ModuleNotFoundError:
    torch = None
    nn = None
    models = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

LABELS = ["AI", "REAL"]
_model = None


def _load_ml_config():
    if torch is None:
        raise RuntimeError("Torch is not installed in the runtime.")
    from ml.config import DEVICE, MODEL_PATH, IMAGE_SIZE, NUM_CLASSES
    return DEVICE, MODEL_PATH, IMAGE_SIZE, NUM_CLASSES

from ml.utils import load_image, load_model


def build_model(num_classes: int):
    model = models.efficientnet_b0(weights=None)
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, num_classes)
    return model


def get_model():
    global _model
    device, model_path, image_size, num_classes = _load_ml_config()

    if _model is None:
        if not os.path.isfile(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")

        model = build_model(num_classes)
        _model = load_model(model, model_path, device)

    return _model, device, image_size


def predict_image(image_path: str) -> dict:
    model, device, image_size = get_model()
    image = load_image(image_path, image_size).to(device)

    with torch.no_grad():
        outputs = model(image)
        probabilities = torch.softmax(outputs, dim=1)[0]
        predicted_index = int(probabilities.argmax().item())
        confidence = float(probabilities[predicted_index].item()) * 100.0

    return {
        "prediction": LABELS[predicted_index],
        "confidence": round(confidence, 2)
    }


def predict_images(image_paths: list[str]) -> list[dict] | None:
    if torch is None:
        raise RuntimeError("Torch is not installed in the runtime.")

    DEVICE, MODEL_PATH, IMAGE_SIZE, NUM_CLASSES = _load_ml_config()
    if not os.path.isfile(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

    # Load once before iterating so model-initialization failures are not
    # silently converted into one empty result for every image.
    get_model()

    results = []
    for image_path in image_paths:
        try:
            results.append(predict_image(image_path))
        except Exception:
            results.append({"prediction": "UNKNOWN", "confidence": None})

    return results
