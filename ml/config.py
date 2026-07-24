import os
import torch

# ==============================
# Dataset Paths
# ==============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TRAIN_DIR = os.path.join(BASE_DIR, "dataset", "train")
VALID_DIR = os.path.join(BASE_DIR, "dataset", "validation")
TEST_DIR = os.path.join(BASE_DIR, "dataset", "test")

# ==============================
# Model Save Path
# ==============================

MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH = os.path.join(MODEL_DIR, "efficientnet_b0.pth")

# ==============================
# Hyperparameters
# ==============================

IMAGE_SIZE = 224
BATCH_SIZE = 32
LEARNING_RATE = 0.0001
NUM_EPOCHS = 1
NUM_CLASSES = 2

# ==============================
# Device
# ==============================

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")