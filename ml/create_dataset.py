import os
import shutil
import random
from pathlib import Path

random.seed(42)

SOURCE = Path(r"C:\Users\spiky\.cache\kagglehub\datasets\birdy654\cifake-real-and-ai-generated-synthetic-images\versions\3")

DEST = Path("dataset")

# Remove old dataset if it exists
if DEST.exists():
    shutil.rmtree(DEST)

for split in ["train", "validation", "test"]:
    for cls in ["ai", "real"]:
        (DEST / split / cls).mkdir(parents=True, exist_ok=True)


def copy_split(src_dir, train_ratio=0.9):
    images = list(src_dir.glob("*"))
    random.shuffle(images)

    split = int(len(images) * train_ratio)

    train_imgs = images[:split]
    val_imgs = images[split:]

    return train_imgs, val_imgs


# ---------- TRAIN ----------
for src_name, dst_name in [("FAKE", "ai"), ("REAL", "real")]:
    train_imgs, val_imgs = copy_split(SOURCE / "train" / src_name)

    for img in train_imgs:
        shutil.copy2(img, DEST / "train" / dst_name / img.name)

    for img in val_imgs:
        shutil.copy2(img, DEST / "validation" / dst_name / img.name)

# ---------- TEST ----------
for src_name, dst_name in [("FAKE", "ai"), ("REAL", "real")]:
    for img in (SOURCE / "test" / src_name).glob("*"):
        shutil.copy2(img, DEST / "test" / dst_name / img.name)

print("Dataset created successfully!")