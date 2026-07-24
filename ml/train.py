import torch
import torch.nn as nn
import torch.optim as optim

from torchvision.models import (
    efficientnet_b0,
    EfficientNet_B0_Weights,
)

from config import (
    DEVICE,
    MODEL_PATH,
    NUM_CLASSES,
    NUM_EPOCHS,
    LEARNING_RATE,
)

from prepare_dataset import build_dataloaders
from utils import save_model


def build_model():

    weights = EfficientNet_B0_Weights.DEFAULT

    model = efficientnet_b0(weights=weights)

    in_features = model.classifier[1].in_features

    model.classifier[1] = nn.Linear(
        in_features,
        NUM_CLASSES
    )

    return model


def train():

    train_loader, valid_loader, _ = build_dataloaders()

    model = build_model().to(DEVICE)

    criterion = nn.CrossEntropyLoss()

    optimizer = optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE
    )

    print("=" * 50)
    print("Training Started")
    print("Device :", DEVICE)
    print("Train Images :", len(train_loader.dataset))
    print("Validation Images :", len(valid_loader.dataset))
    print("=" * 50)

    for epoch in range(NUM_EPOCHS):

        print(f"\nEpoch {epoch + 1}/{NUM_EPOCHS}")

        model.train()

        running_loss = 0
        running_correct = 0

        for batch_idx, (images, labels) in enumerate(train_loader):

            images = images.to(DEVICE)
            labels = labels.to(DEVICE)

            optimizer.zero_grad()

            outputs = model(images)

            # ---------------- DEBUG ----------------
            if batch_idx == 0:
                print("\n========== DEBUG ==========")
                print("Output Shape :", outputs.shape)
                print("Labels Shape :", labels.shape)
                print("Labels :", labels)
                print("Unique Labels :", torch.unique(labels))
                print("Min Label :", labels.min().item())
                print("Max Label :", labels.max().item())
                print("===========================\n")
            # ---------------------------------------

            loss = criterion(outputs, labels)

            loss.backward()

            optimizer.step()

            _, predicted = torch.max(outputs, 1)

            running_loss += loss.item()

            running_correct += (predicted == labels).sum().item()

            if batch_idx % 100 == 0:

                print(
                    f"Batch {batch_idx}/{len(train_loader)} "
                    f"Loss={loss.item():.4f}"
                )

        train_loss = running_loss / len(train_loader)

        train_acc = running_correct / len(train_loader.dataset)

        print(f"\nTrain Loss : {train_loss:.4f}")
        print(f"Train Accuracy : {train_acc:.4f}")

        model.eval()

        val_loss = 0
        val_correct = 0

        with torch.no_grad():

            for images, labels in valid_loader:

                images = images.to(DEVICE)
                labels = labels.to(DEVICE)

                outputs = model(images)

                loss = criterion(outputs, labels)

                val_loss += loss.item()

                _, predicted = torch.max(outputs, 1)

                val_correct += (
                    predicted == labels
                ).sum().item()

        val_loss /= len(valid_loader)

        val_acc = val_correct / len(valid_loader.dataset)

        print(f"Validation Loss : {val_loss:.4f}")
        print(f"Validation Accuracy : {val_acc:.4f}")

    save_model(model, MODEL_PATH)

    print("\nTraining Finished")
    print("Model Saved :", MODEL_PATH)


if __name__ == "__main__":
    train()