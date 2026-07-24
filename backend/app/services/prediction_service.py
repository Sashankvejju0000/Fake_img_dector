import os
import sys

import torch
import torch.nn as nn
from torchvision import models

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.config import DEVICE, MODEL_PATH, IMAGE_SIZE, NUM_CLASSES
from ml.utils import load_image, load_model

LABELS = ["FAKE", "REAL"]
_model = None


def build_model():
    model = models.efficientnet_b0(weights=None)
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, NUM_CLASSES)
    return model


def get_model():
    global _model

    if _model is None:
        if not os.path.isfile(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

        model = build_model()
        _model = load_model(model, MODEL_PATH, DEVICE)

    return _model


def predict_image(image_path: str) -> dict:
    model = get_model()
    image = load_image(image_path, IMAGE_SIZE).to(DEVICE)

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
    if not os.path.isfile(MODEL_PATH):
        return None

    results = []
    for image_path in image_paths:
        try:
            results.append(predict_image(image_path))
        except Exception:
            results.append({"prediction": None, "confidence": None})

    return results
