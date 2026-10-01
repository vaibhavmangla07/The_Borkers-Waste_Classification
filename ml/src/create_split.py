import os
import json
import csv
import hashlib
import random
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt
from tqdm import tqdm
from collections import defaultdict
import numpy as np

# Reproducibility
random.seed(42)
np.random.seed(42)

def calculate_md5(filepath):
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def create_split():
    dataset_dir = Path("ml/garbage_classification_dataset")
    data_dir = Path("ml/data")
    reports_dir = Path("ml/reports")
    config_path = Path("ml/config/class_mapping.json")

    data_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    with open(config_path, "r") as f:
        config = json.load(f)
    
    mapping = config.get("dataset_to_application", {})
    excluded = config.get("excluded_classes", [])

    print("Mapping configuration:")
    for k, v in mapping.items():
        print(f"  {k} -> {v}")

    # Gather valid files
    dataset_classes = [d.name for d in dataset_dir.iterdir() if d.is_dir()]
    
    valid_images = []
    
    print("\nScanning dataset for valid images and hashing...")
    for class_name in dataset_classes:
        if class_name in excluded:
            continue
            
        app_cat = mapping.get(class_name)
        if not app_cat:
            continue
            
        class_dir = dataset_dir / class_name
        for file in tqdm(list(class_dir.iterdir()), desc=f"Scanning {class_name}"):
            if not file.is_file():
                continue
                
            ext = file.suffix.lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.webp', '.bmp']:
                continue
                
            try:
                with Image.open(file) as img:
                    img.verify()
                with Image.open(file) as img:
                    img.load()
            except Exception:
                continue
                
            file_hash = calculate_md5(file)
            
            # Using relative path from ml/ directory as requested
            # e.g., garbage_classification_dataset/plastic/img1.jpg
            rel_path = file.relative_to(Path("ml").absolute()) if file.is_absolute() else file.relative_to(Path("ml")) if "ml" in str(file) else Path(*file.parts[1:])
            # Actually, we run this inside 'The_Brokers-Waste_Classification', so file is 'ml/garbage_classification_dataset/...'
            # We want 'garbage_classification_dataset/...'
            rel_path = file.relative_to("ml")
            
            valid_images.append({
                "image_path": str(rel_path),
                "original_class": class_name,
                "application_category": app_cat,
                "file_hash": file_hash
            })

    # Group by hash to prevent leakage
    hash_groups = defaultdict(list)
    for img in valid_images:
        hash_groups[img["file_hash"]].append(img)
        
    # Now group by application category
    cat_to_groups = defaultdict(list)
    for h, imgs in hash_groups.items():
        # A hash should only have one application category (unless images from diff classes are identical)
        # We assign the group to the category of its first image
        app_cat = imgs[0]["application_category"]
        cat_to_groups[app_cat].append(imgs)
        
    train_split = []
    val_split = []
    test_split = []
    
    print("\nSplitting by category...")
    
    split_counts = {
        "train": defaultdict(int),
        "validation": defaultdict(int),
        "test": defaultdict(int)
    }

    for cat, groups in cat_to_groups.items():
        # Sort groups by hash to ensure determinism before shuffling
        groups.sort(key=lambda x: x[0]["file_hash"])
        random.shuffle(groups)
        
        n_groups = len(groups)
        n_train = int(n_groups * 0.70)
        n_val = int(n_groups * 0.15)
        
        train_groups = groups[:n_train]
        val_groups = groups[n_train:n_train+n_val]
        test_groups = groups[n_train+n_val:]
        
        for g in train_groups:
            # Optionally just take the first duplicate and ignore the rest in metadata
            # "Preferably, if practical: remove duplicate copies from training metadata while keeping the raw dataset untouched."
            img = g[0]
            img["split"] = "train"
            train_split.append(img)
            split_counts["train"][cat] += 1
            
        for g in val_groups:
            img = g[0]
            img["split"] = "validation"
            val_split.append(img)
            split_counts["validation"][cat] += 1
            
        for g in test_groups:
            img = g[0]
            img["split"] = "test"
            test_split.append(img)
            split_counts["test"][cat] += 1

    all_splits = train_split + val_split + test_split
    
    # Write Manifest
    manifest_path = data_dir / "dataset_manifest.csv"
    with open(manifest_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["image_path", "original_class", "application_category", "split", "file_hash"])
        writer.writeheader()
        for img in all_splits:
            writer.writerow(img)
            
    print(f"\nManifest written to {manifest_path}")
    
    # Write Split Report
    report = {
        "seed": 42,
        "total_usable_images": len(all_splits),
        "train_count": len(train_split),
        "validation_count": len(val_split),
        "test_count": len(test_split),
        "train": dict(split_counts["train"]),
        "validation": dict(split_counts["validation"]),
        "test": dict(split_counts["test"])
    }
    
    with open(reports_dir / "split_report.json", "w") as f:
        json.dump(report, f, indent=4)
        
    # Write Markdown
    md_content = f"""# Dataset Split Report

## Dataset
ml/garbage_classification_dataset

## Total usable images
{report['total_usable_images']}

## Training set
{report['train_count']} images ({report['train_count']/report['total_usable_images']*100:.1f}%)

## Validation set
{report['validation_count']} images ({report['validation_count']/report['total_usable_images']*100:.1f}%)

## Test set
{report['test_count']} images ({report['test_count']/report['total_usable_images']*100:.1f}%)

## Class distribution
| Category | Train | Validation | Test | Total |
|---|---|---|---|---|
"""
    all_cats = sorted(list(cat_to_groups.keys()))
    for cat in all_cats:
        tr = split_counts["train"][cat]
        va = split_counts["validation"][cat]
        te = split_counts["test"][cat]
        tot = tr + va + te
        md_content += f"| {cat} | {tr} | {va} | {te} | {tot} |\n"
        
    md_content += f"""
## Excluded classes
{', '.join(excluded) if excluded else 'None'}

## Duplicate handling
Exact duplicates grouped by MD5 hash. Only the first image of a duplicate group is included in the manifest. Duplicate groups are kept strictly within a single split (train/val/test) to prevent data leakage.

## Random seed
42

## Leakage checks
Data leakage prevented by strict hash-based grouping prior to split allocation.
"""
    with open(reports_dir / "SPLIT_REPORT.md", "w") as f:
        f.write(md_content)

    # Plot Distribution
    plt.figure(figsize=(12, 6))
    
    ind = np.arange(len(all_cats))
    width = 0.25
    
    tr_vals = [split_counts["train"][c] for c in all_cats]
    va_vals = [split_counts["validation"][c] for c in all_cats]
    te_vals = [split_counts["test"][c] for c in all_cats]
    
    plt.bar(ind, tr_vals, width, label='Train')
    plt.bar(ind + width, va_vals, width, label='Validation')
    plt.bar(ind + width*2, te_vals, width, label='Test')
    
    plt.ylabel('Number of Images')
    plt.title('Split Distribution by Application Category')
    plt.xticks(ind + width, all_cats, rotation=45, ha='right')
    plt.legend(loc='best')
    plt.tight_layout()
    plt.savefig(reports_dir / "split_distribution.png")
    plt.close()
    
    print(f"Reports generated in {reports_dir}")
    
    # Check if all 8 categories exist
    expected_categories = {"plastic", "paper", "cardboard", "glass", "metal", "organic", "e-waste", "other"}
    missing = expected_categories - set(all_cats)
    if missing:
        print(f"\nWARNING: Missing categories: {missing}")

if __name__ == "__main__":
    create_split()
