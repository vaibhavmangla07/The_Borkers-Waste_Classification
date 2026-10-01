import json
from pathlib import Path
from app.database.session import SessionLocal
from app.models.waste_category import WasteCategory

def test_class_names_match_db_seed():
    classes_path = Path("artifacts/classes.json")
    if not classes_path.exists():
        return  # Model not fully available yet, but if it exists we check
        
    with open(classes_path, "r") as f:
        model_classes = json.load(f)
        
    db = SessionLocal()
    try:
        db_categories = db.query(WasteCategory).all()
        db_slugs = {cat.slug for cat in db_categories}
        
        # Check if all model classes exist in DB
        for model_class in model_classes:
            assert model_class in db_slugs, f"Model class '{model_class}' not found in database categories"
    finally:
        db.close()
