from app.ml.process_images import process_all_images

images = process_all_images("uploads")

print(f"\nTotal Images : {len(images)}\n")

for img in images:

    print(img["filename"])

    print(img["tensor"].shape)

    print("--------------------------")