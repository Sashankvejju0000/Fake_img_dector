import os

from app.ml.process_images import process_all_images

print("Current Working Directory:")
print(os.getcwd())

print("\nFiles in current directory:")
print(os.listdir())

print("\nUploads exists:", os.path.exists("uploads"))

if os.path.exists("uploads"):
    print("\nFiles inside uploads:")
    print(os.listdir("uploads"))

images = process_all_images("uploads")

print(f"\nTotal Images : {len(images)}\n")

for img in images:
    print(img["filename"])
    print(img["tensor"].shape)
    print("--------------------------")
