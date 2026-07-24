import os
import random
import shutil

# Source CIFAKE dataset
SOURCE = r"C:\Users\spiky\.cache\kagglehub\datasets\birdy654\cifake-real-and-ai-generated-synthetic-images\versions\3"

# Destination dataset
DEST = r"D:\Fake_img_dector-main\ml\dataset"

# Images required
TRAIN_PER_CLASS = 4000
VAL_PER_CLASS = 500
TEST_PER_CLASS = 500

random.seed(42)

for split in ["train", "validation", "test"]:
    for cls in ["fake", "real"]:
        os.makedirs(os.path.join(DEST, split, cls), exist_ok=True)


def copy_images(src_folder, cls_name):
    images = [
        f for f in os.listdir(src_folder)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    random.shuffle(images)

    train = images[:TRAIN_PER_CLASS]
    val = images[TRAIN_PER_CLASS:TRAIN_PER_CLASS + VAL_PER_CLASS]
    test = images[TRAIN_PER_CLASS + VAL_PER_CLASS:
                  TRAIN_PER_CLASS + VAL_PER_CLASS + TEST_PER_CLASS]

    for img in train:
        shutil.copy2(
            os.path.join(src_folder, img),
            os.path.join(DEST, "train", cls_name, img)
        )

    for img in val:
        shutil.copy2(
            os.path.join(src_folder, img),
            os.path.join(DEST, "validation", cls_name, img)
        )

    for img in test:
        shutil.copy2(
            os.path.join(src_folder, img),
            os.path.join(DEST, "test", cls_name, img)
        )


print("Processing FAKE...")
copy_images(os.path.join(SOURCE, "train", "FAKE"), "fake")

print("Processing REAL...")
copy_images(os.path.join(SOURCE, "train", "REAL"), "real")

print("\nDone!")
print("Dataset created at:")
print(DEST)