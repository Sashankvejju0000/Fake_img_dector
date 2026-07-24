import os

from torchvision import transforms
from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader

from config import (
    TRAIN_DIR,
    VALID_DIR,
    TEST_DIR,
    IMAGE_SIZE,
    BATCH_SIZE,
)


def get_transforms(train=True):

    if train:
        return transforms.Compose([
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(10),
            transforms.ToTensor(),
            transforms.Normalize(
                [0.485, 0.456, 0.406],
                [0.229, 0.224, 0.225]
            ),
        ])

    return transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(
            [0.485, 0.456, 0.406],
            [0.229, 0.224, 0.225]
        ),
    ])


def verify_directories():

    for folder in [TRAIN_DIR, VALID_DIR, TEST_DIR]:

        if not os.path.exists(folder):
            raise FileNotFoundError(folder)


def build_datasets():

    verify_directories()

    train_dataset = ImageFolder(
        TRAIN_DIR,
        transform=get_transforms(True)
    )

    valid_dataset = ImageFolder(
        VALID_DIR,
        transform=get_transforms(False)
    )

    test_dataset = ImageFolder(
        TEST_DIR,
        transform=get_transforms(False)
    )

    return train_dataset, valid_dataset, test_dataset


def build_dataloaders():

    train_dataset, valid_dataset, test_dataset = build_datasets()

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0,
        pin_memory=False
    )

    valid_loader = DataLoader(
        valid_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0,
        pin_memory=False
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0,
        pin_memory=False
    )

    return train_loader, valid_loader, test_loader


def dataset_summary(dataset):

    summary = {}

    for _, label in dataset.samples:

        name = dataset.classes[label]

        summary[name] = summary.get(name, 0) + 1

    return summary


if __name__ == "__main__":

    train_dataset, valid_dataset, test_dataset = build_datasets()

    print("Train:", dataset_summary(train_dataset))
    print("Validation:", dataset_summary(valid_dataset))
    print("Test:", dataset_summary(test_dataset))