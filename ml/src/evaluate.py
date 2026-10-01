import json
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import seaborn as sns

from dataset import WasteDataset, TARGET_CLASSES
from model import get_model
from metrics import calculate_metrics
from utils import set_seed, get_device
from train import evaluate

def generate_training_curves(history_path, output_path):
    with open(history_path, 'r') as f:
        data = json.load(f)["epochs"]
        
    epochs = [d["epoch"] for d in data]
    train_loss = [d["train_loss"] for d in data]
    val_loss = [d["val_loss"] for d in data]
    val_acc = [d["val_accuracy"] for d in data]
    val_f1 = [d["val_macro_f1"] for d in data]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Loss
    ax1.plot(epochs, train_loss, label='Train Loss', marker='o')
    ax1.plot(epochs, val_loss, label='Val Loss', marker='s')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.set_title('Training & Validation Loss')
    ax1.legend()
    ax1.grid(True, linestyle='--', alpha=0.7)
    
    # Metrics
    ax2.plot(epochs, val_acc, label='Val Accuracy', marker='^')
    ax2.plot(epochs, val_f1, label='Val Macro F1', marker='d')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Score')
    ax2.set_title('Validation Metrics')
    ax2.legend()
    ax2.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def plot_confusion_matrix(y_true, y_pred, classes, output_path):
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=classes, yticklabels=classes)
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title('Test Set Confusion Matrix')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def main():
    set_seed(42)
    device = get_device()
    
    artifacts_dir = Path("ml/artifacts")
    reports_dir = Path("ml/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    manifest_path = "ml/data/dataset_manifest.csv"
    test_dataset = WasteDataset(manifest_path, "test", is_train=False)
    batch_size = 32 if device.type in ["cuda", "mps"] else 16
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    model = get_model(num_classes=8)
    model.load_state_dict(torch.load(artifacts_dir / "best_model.pt", map_location=device, weights_only=True))
    model.to(device)
    
    criterion = nn.CrossEntropyLoss()
    
    print("Evaluating on test set...")
    test_loss, test_metrics = evaluate(model, test_loader, criterion, device)
    
    # Also get raw predictions for confusion matrix
    model.eval()
    all_preds = []
    all_targets = []
    with torch.no_grad():
        for inputs, targets in test_loader:
            inputs = inputs.to(device)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_targets.extend(targets.cpu().numpy())
            
    plot_confusion_matrix(all_targets, all_preds, TARGET_CLASSES, reports_dir / "confusion_matrix.png")
    generate_training_curves(artifacts_dir / "training_history.json", reports_dir / "training_history.png")
    
    # Classification report format
    cls_report = {}
    for i, cls in enumerate(TARGET_CLASSES):
        cls_report[cls] = {
            "precision": test_metrics["per_class"]["precision"][i],
            "recall": test_metrics["per_class"]["recall"][i],
            "f1": test_metrics["per_class"]["f1"][i]
        }
        
    with open(reports_dir / "classification_report.json", "w") as f:
        json.dump(cls_report, f, indent=2)
        
    # Save test metrics
    with open(artifacts_dir / "test_metrics.json", "w") as f:
        json.dump({"loss": test_loss, **test_metrics}, f, indent=2)
        
    # Update metadata
    with open(artifacts_dir / "model_metadata.json", "r") as f:
        metadata = json.load(f)
        
    metadata["test_images"] = len(test_dataset)
    metadata["test_accuracy"] = test_metrics["accuracy"]
    metadata["test_macro_f1"] = test_metrics["macro_f1"]
    metadata["test_top3_accuracy"] = test_metrics["top3_accuracy"]
    
    with open(artifacts_dir / "model_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
        
    # Generate Markdown Report
    with open(artifacts_dir / "training_history.json", "r") as f:
        history = json.load(f)["epochs"]
        
    with open(reports_dir / "TRAINING_REPORT.md", "w") as f:
        f.write(f"""# EcoVision AI - Training Report

## Objective
Train a waste classification model mapping images to 8 application categories.

## Dataset & Split
- Total Train Images: {metadata['train_images']}
- Total Validation Images: {metadata['validation_images']}
- Total Test Images: {metadata['test_images']}
- 8 Categories: {', '.join(TARGET_CLASSES)}

## Imbalance Handling
Weighted CrossEntropyLoss computed from training split distribution.

## Model
- Architecture: {metadata['architecture']}
- Pretrained Weights: {metadata['pretrained_weights']}
- Input Size: {metadata['image_size']}
- Device: {metadata['device_used']}
- Seed: {metadata['seed']}

## Training
Stage 1 (Classifier): 5 epochs
Stage 2 (Fine-tuning): 3 epochs (Top 2 blocks unfreezed)
Best Validation Macro F1: {metadata['best_validation_macro_f1']:.4f}

## Test Performance
- Accuracy: {metadata['test_accuracy']:.4f}
- Top-3 Accuracy: {metadata['test_top3_accuracy']:.4f}
- Macro F1: {metadata['test_macro_f1']:.4f}

## Backend Integration
The model artifact is saved in `ml/artifacts/best_model.pt`. It's a raw state dict. The backend predictor will need to initialize an EfficientNet-B0 backbone with an 8-class linear classifier and load these weights. Classes mapping matches exactly with `ml/artifacts/classes.json`.
""")

    print(f"Test Accuracy: {test_metrics['accuracy']:.4f}")
    print(f"Test Macro F1: {test_metrics['macro_f1']:.4f}")
    print(f"Test Top-3: {test_metrics['top3_accuracy']:.4f}")
    print("\nEvaluation complete! Artifacts and reports generated.")

if __name__ == "__main__":
    main()
