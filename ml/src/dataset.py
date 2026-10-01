import csv
import torch
from pathlib import Path
from PIL import Image
from torch.utils.data import Dataset
import torchvision.transforms as transforms

TARGET_CLASSES = [
    "plastic",
    "paper",
    "cardboard",
    "glass",
    "metal",
    "organic",
    "e-waste",
    "other"
]

class WasteDataset(Dataset):
    def __init__(self, manifest_path, split, is_train=False):
        self.split = split
        self.is_train = is_train
        
        # Load rows for this split
        self.data = []
        with open(manifest_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['split'] == split:
                    # Validate class exists
                    if row['application_category'] not in TARGET_CLASSES:
                        raise ValueError(f"Unknown category {row['application_category']}")
                    self.data.append({
                        "image_path": Path("ml") / row["image_path"],
                        "class_idx": TARGET_CLASSES.index(row['application_category'])
                    })

        if not self.data:
            raise ValueError(f"No data found for split: {split}")

        # ImageNet normalization used by EfficientNet
        normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                         std=[0.229, 0.224, 0.225])

        if self.is_train:
            self.transform = transforms.Compose([
                transforms.Resize(256),
                transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
                transforms.RandomHorizontalFlip(),
                transforms.RandomRotation(15),
                transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1),
                transforms.ToTensor(),
                normalize
            ])
        else:
            self.transform = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                normalize
            ])

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        img_path = item["image_path"]
        
        try:
            with Image.open(img_path) as img:
                img = img.convert('RGB')
        except Exception as e:
            raise RuntimeError(f"Error opening image {img_path}: {e}")

        img_tensor = self.transform(img)
        return img_tensor, item["class_idx"]
