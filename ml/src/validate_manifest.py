import csv
import json
from pathlib import Path
from PIL import Image

def validate_manifest():
    manifest_path = Path("ml/data/dataset_manifest.csv")
    config_path = Path("ml/config/class_mapping.json")
    
    with open(config_path, "r") as f:
        config = json.load(f)
        
    excluded = config.get("excluded_classes", [])
    valid_splits = {"train", "validation", "test"}
    valid_categories = {"plastic", "paper", "cardboard", "glass", "metal", "organic", "e-waste", "other"}
    
    hashes = {}
    
    with open(manifest_path, "r") as f:
        reader = csv.DictReader(f)
        
        for idx, row in enumerate(reader):
            img_path = Path("ml") / row["image_path"]
            app_cat = row["application_category"]
            orig_class = row["original_class"]
            split = row["split"]
            fhash = row["file_hash"]
            
            # Check path exists
            assert img_path.exists(), f"Image not found: {img_path}"
            assert not img_path.is_absolute(), f"Absolute path found: {row['image_path']}"
            
            # Check if readable
            try:
                with Image.open(img_path) as img:
                    img.verify()
            except Exception as e:
                raise AssertionError(f"Image {img_path} is unreadable: {e}")
                
            # Check application category
            assert app_cat in valid_categories, f"Invalid application category {app_cat}"
            
            # Check split
            assert split in valid_splits, f"Invalid split {split}"
            
            # Check excluded
            assert orig_class not in excluded, f"Excluded class {orig_class} included"
            
            # Check leakage
            if fhash in hashes:
                assert hashes[fhash] == split, f"Data leakage detected! Hash {fhash} is in {hashes[fhash]} and {split}"
            else:
                hashes[fhash] = split

    print("Manifest validation passed successfully.")

if __name__ == "__main__":
    validate_manifest()
