import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from app.ai.predictor import Predictor
from PIL import Image

def run_smoke_test():
    dataset_dir = Path(__file__).parent.parent / "ml/garbage_classification_dataset"
    
    test_images = [
        ("plastic", dataset_dir / "plastic" / "plastic1.jpg"),
        ("paper", dataset_dir / "paper" / "paper1.jpg"),
        ("cardboard", dataset_dir / "cardboard" / "cardboard1.jpg")
    ]
    
    print("--- REAL IMAGE SMOKE TEST ---")
    
    for category, path in test_images:
        # Fallback to any file if standard one doesn't exist
        if not path.exists():
            files = list((dataset_dir / category).glob("*.jpg"))
            if files:
                path = files[0]
            else:
                print(f"Skipping {category}, no image found")
                continue
                
        print(f"\nProcessing: {path.name}")
        print(f"Expected category: {category}")
        
        try:
            img = Image.open(path)
            response = Predictor.predict(img)
            
            top_prediction = response.predictions[0]
            print(f"Top-1 Prediction: {top_prediction.label} (confidence: {top_prediction.confidence:.4f})")
            print("Top-3 Predictions:")
            for p in response.predictions:
                print(f"  {p.rank}. {p.label}: {p.confidence:.4f}")
        except Exception as e:
            print(f"Error processing {path.name}: {e}")

if __name__ == "__main__":
    run_smoke_test()
