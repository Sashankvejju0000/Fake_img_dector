import os
import kagglehub

path = kagglehub.dataset_download(
    "birdy654/cifake-real-and-ai-generated-synthetic-images"
)

print("Dataset Path:", path)
print()

for root, dirs, files in os.walk(path):
    print(root)