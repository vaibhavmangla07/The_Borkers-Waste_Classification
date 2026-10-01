import os
import json
import hashlib
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt
from tqdm import tqdm
from collections import defaultdict

def calculate_md5(filepath):
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def inspect_dataset():
    dataset_dir = Path("ml/garbage_classification_dataset")
    reports_dir = Path("ml/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    print(f"Inspecting dataset at {dataset_dir}...")
    
    classes = [d.name for d in dataset_dir.iterdir() if d.is_dir()]
    print(f"Found classes: {classes}")

    stats = {
        "dataset_path": str(dataset_dir),
        "total_files": 0,
        "total_images": 0,
        "valid_images": 0,
        "corrupted_images": [],
        "classes": classes,
        "class_counts": defaultdict(int),
        "image_formats": defaultdict(int),
        "dimensions": {
            "min_width": float('inf'), "max_width": 0,
            "min_height": float('inf'), "max_height": 0,
            "sum_width": 0, "sum_height": 0
        },
        "duplicate_statistics": {
            "exact_duplicate_groups": 0,
            "number_of_duplicate_files": 0
        }
    }
    
    hashes = defaultdict(list)
    common_dims = defaultdict(int)

    # Sample images for visualization
    class_samples = defaultdict(list)

    # Traverse directory
    for class_name in classes:
        class_dir = dataset_dir / class_name
        for file in tqdm(class_dir.iterdir(), desc=f"Scanning {class_name}"):
            if not file.is_file():
                continue
            
            stats["total_files"] += 1
            ext = file.suffix.lower()
            stats["image_formats"][ext] += 1
            
            # Simple check if it's an image extension
            if ext not in ['.jpg', '.jpeg', '.png', '.webp', '.bmp']:
                continue
                
            stats["total_images"] += 1
            stats["class_counts"][class_name] += 1

            # Check if valid
            try:
                with Image.open(file) as img:
                    img.verify()
                # Image.verify doesn't always catch everything, open again to get dimensions
                with Image.open(file) as img:
                    w, h = img.size
                    stats["valid_images"] += 1
                    
                    # Update dimensions
                    stats["dimensions"]["min_width"] = min(stats["dimensions"]["min_width"], w)
                    stats["dimensions"]["max_width"] = max(stats["dimensions"]["max_width"], w)
                    stats["dimensions"]["min_height"] = min(stats["dimensions"]["min_height"], h)
                    stats["dimensions"]["max_height"] = max(stats["dimensions"]["max_height"], h)
                    stats["dimensions"]["sum_width"] += w
                    stats["dimensions"]["sum_height"] += h
                    common_dims[f"{w}x{h}"] += 1

                    if len(class_samples[class_name]) < 5:
                        class_samples[class_name].append(file)
                        
            except Exception as e:
                stats["corrupted_images"].append(str(file))
                continue
            
            # Duplicate check
            file_hash = calculate_md5(file)
            hashes[file_hash].append(str(file))

    # Process duplicates
    duplicates = {k: v for k, v in hashes.items() if len(v) > 1}
    stats["duplicate_statistics"]["exact_duplicate_groups"] = len(duplicates)
    stats["duplicate_statistics"]["number_of_duplicate_files"] = sum(len(v) - 1 for v in duplicates.values())

    # Finalize dimensions
    v_img_count = stats["valid_images"]
    if v_img_count > 0:
        stats["dimensions"]["avg_width"] = stats["dimensions"]["sum_width"] / v_img_count
        stats["dimensions"]["avg_height"] = stats["dimensions"]["sum_height"] / v_img_count
    
    most_common_dim = max(common_dims.items(), key=lambda x: x[1]) if common_dims else ("N/A", 0)
    stats["dimensions"]["most_common"] = most_common_dim

    # Sort class counts
    stats["class_counts"] = dict(sorted(stats["class_counts"].items(), key=lambda item: item[1], reverse=True))

    # --- Generate Reports ---

    # JSON Report
    with open(reports_dir / "dataset_report.json", "w") as f:
        json.dump(stats, f, indent=4)

    # Class Distribution Chart
    plt.figure(figsize=(10, 6))
    plt.bar(stats["class_counts"].keys(), stats["class_counts"].values())
    plt.xticks(rotation=45, ha="right")
    plt.ylabel('Number of Images')
    plt.title('Class Distribution')
    plt.tight_layout()
    plt.savefig(reports_dir / "class_distribution.png")
    plt.close()

    # Visual Sample Grid
    fig, axes = plt.subplots(len(classes), 5, figsize=(15, 3 * len(classes)))
    fig.suptitle("Dataset Samples (5 per class)", fontsize=16)
    
    # Check if axes is 1D (when there's only 1 class)
    if len(classes) == 1:
        axes = [axes]
        
    for i, class_name in enumerate(classes):
        samples = class_samples[class_name]
        for j in range(5):
            ax = axes[i][j]
            ax.axis('off')
            if j < len(samples):
                try:
                    img = Image.open(samples[j])
                    ax.imshow(img)
                    if j == 0:
                        ax.set_title(class_name, loc='left')
                except:
                    pass

    plt.tight_layout()
    plt.savefig(reports_dir / "dataset_samples.png")
    plt.close()

    # MD Report
    md_content = f"""# EcoVision AI Dataset Report

## Dataset
- **Path:** `{stats["dataset_path"]}`
- **Total Files:** {stats["total_files"]}
- **Total Images:** {stats["total_images"]}
- **Valid Images:** {stats["valid_images"]}

## Classes
Total classes: {len(stats["classes"])}
{', '.join(stats["classes"])}

## Class Distribution
"""
    for cls, count in stats["class_counts"].items():
        pct = (count / stats["valid_images"] * 100) if stats["valid_images"] > 0 else 0
        md_content += f"- **{cls}:** {count} images ({pct:.2f}%)\n"

    md_content += f"""
## Corrupted Images
- **Total Corrupted:** {len(stats["corrupted_images"])}
"""
    for corrupted in stats["corrupted_images"][:10]:
        md_content += f"  - `{corrupted}`\n"
    if len(stats["corrupted_images"]) > 10:
        md_content += f"  - ...and {len(stats['corrupted_images']) - 10} more\n"

    md_content += f"""
## Duplicate Images
- **Exact Duplicate Groups:** {stats["duplicate_statistics"]["exact_duplicate_groups"]}
- **Number of Duplicate Files:** {stats["duplicate_statistics"]["number_of_duplicate_files"]}

## Image Dimensions
- **Minimum:** {stats['dimensions']['min_width']}x{stats['dimensions']['min_height']}
- **Maximum:** {stats['dimensions']['max_width']}x{stats['dimensions']['max_height']}
- **Average:** {stats['dimensions'].get('avg_width', 0):.1f}x{stats['dimensions'].get('avg_height', 0):.1f}
- **Most Common:** {stats['dimensions']['most_common'][0]} ({stats['dimensions']['most_common'][1]} images)

## Observations
- Image formats found: {dict(stats['image_formats'])}
- Mappings should be reviewed in `ml/config/class_mapping.json`.
"""

    with open(reports_dir / "DATASET_REPORT.md", "w") as f:
        f.write(md_content)

    print("Inspection complete. Reports generated in ml/reports/")

if __name__ == "__main__":
    inspect_dataset()
