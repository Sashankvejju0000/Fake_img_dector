import os
import torch
import torch.nn as nn
from torchvision import models

from config import DEVICE, MODEL_PATH, IMAGE_SIZE, NUM_CLASSES
from utils import load_image, load_model


def build_model():
    model = models.efficientnet_b0(weights=None)
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, NUM_CLASSES)
    return model


def predict(image_path: str):
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    model = build_model()
    model = load_model(model, MODEL_PATH, DEVICE)

    image = load_image(image_path, IMAGE_SIZE).to(DEVICE)
    with torch.no_grad():
        outputs = model(image)
        probabilities = torch.softmax(outputs, dim=1)[0]
        predicted_index = probabilities.argmax().item()

    return {
        "label_index": predicted_index,
        "probability": float(probabilities[predicted_index].item()),
        "scores": probabilities.tolist()
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Predict image class")
    parser.add_argument("image_path", type=str, help="Path to the input image")
    args = parser.parse_args()

    result = predict(args.image_path)
    print(result)
