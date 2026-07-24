from prepare_dataset import build_datasets

train_dataset, valid_dataset, test_dataset = build_datasets()

print("Classes:", train_dataset.classes)
print("Class to idx:", train_dataset.class_to_idx)

labels = set()

for _, label in train_dataset.samples:
    labels.add(label)

print("Labels found:", sorted(labels))