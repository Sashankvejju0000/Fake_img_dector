import torch
import torch.nn as nn
from torchvision import models

from config import DEVICE, MODEL_PATH, NUM_CLASSES
from prepare_dataset import build_dataloaders


def build_model():
    model = models.efficientnet_b0(weights=None)
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, NUM_CLASSES)
    return model


def test():
    _, _, test_loader = build_dataloaders()
    model = build_model().to(DEVICE)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.eval()

    total = 0
    correct = 0
    losses = 0.0

    criterion = nn.CrossEntropyLoss()

    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(DEVICE)
            labels = labels.to(DEVICE)

            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            loss = criterion(outputs, labels)

            total += labels.size(0)
            correct += torch.sum(preds == labels.data)
            losses += loss.item() * inputs.size(0)

    accuracy = correct.double() / total
    average_loss = losses / total

    print(f"Test loss: {average_loss:.4f}")
    print(f"Test accuracy: {accuracy:.4f}")


if __name__ == "__main__":
    test()
