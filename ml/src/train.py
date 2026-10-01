import os
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
from datetime import datetime
from pathlib import Path
from tqdm import tqdm

from dataset import WasteDataset, TARGET_CLASSES
from model import get_model, freeze_backbone, unfreeze_feature_blocks
from metrics import calculate_metrics
from utils import set_seed, get_device

def train_one_epoch(model, dataloader, criterion, optimizer, device):
    model.train()
    total_loss = 0.0
    all_preds = []
    all_targets = []
    
    for inputs, targets in tqdm(dataloader, desc="Training", leave=False):
        inputs, targets = inputs.to(device), targets.to(device)
        
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item() * inputs.size(0)
        _, preds = torch.max(outputs, 1)
        
        all_preds.extend(preds.cpu().numpy())
        all_targets.extend(targets.cpu().numpy())
        
    epoch_loss = total_loss / len(dataloader.dataset)
    epoch_acc = np.mean(np.array(all_preds) == np.array(all_targets))
    
    return epoch_loss, epoch_acc

def evaluate(model, dataloader, criterion, device):
    model.eval()
    total_loss = 0.0
    all_preds = []
    all_targets = []
    all_probs = []
    
    with torch.no_grad():
        for inputs, targets in tqdm(dataloader, desc="Evaluating", leave=False):
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            
            total_loss += loss.item() * inputs.size(0)
            probs = torch.softmax(outputs, dim=1)
            _, preds = torch.max(outputs, 1)
            
            all_preds.extend(preds.cpu().numpy())
            all_targets.extend(targets.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())
            
    epoch_loss = total_loss / len(dataloader.dataset)
    metrics = calculate_metrics(np.array(all_targets), np.array(all_preds), np.array(all_probs))
    
    return epoch_loss, metrics

def train_stage(model, stage_name, num_epochs, train_loader, val_loader, criterion, optimizer, device, artifacts_dir, start_epoch, best_val_f1):
    history = []
    
    for epoch in range(num_epochs):
        print(f"\n--- Epoch {start_epoch + epoch + 1} ({stage_name}) ---")
        
        train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_metrics = evaluate(model, val_loader, criterion, device)
        
        val_f1 = val_metrics["macro_f1"]
        val_acc = val_metrics["accuracy"]
        val_top3 = val_metrics["top3_accuracy"]
        
        print(f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f}")
        print(f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f} | Val Macro F1: {val_f1:.4f} | Val Top-3: {val_top3:.4f}")
        
        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            print(">>> New best model! Saving...")
            torch.save(model.state_dict(), artifacts_dir / "best_model.pt")
            
        history.append({
            "epoch": start_epoch + epoch + 1,
            "stage": stage_name,
            "train_loss": train_loss,
            "train_accuracy": train_acc,
            "val_loss": val_loss,
            "val_accuracy": val_acc,
            "val_macro_precision": val_metrics["macro_precision"],
            "val_macro_recall": val_metrics["macro_recall"],
            "val_macro_f1": val_f1,
            "val_top3_accuracy": val_top3
        })
        
    return history, best_val_f1

def main():
    set_seed(42)
    device = get_device()
    print(f"Using device: {device}")
    
    # Paths
    manifest_path = "ml/data/dataset_manifest.csv"
    artifacts_dir = Path("ml/artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    # Save classes
    with open(artifacts_dir / "classes.json", "w") as f:
        json.dump({"classes": TARGET_CLASSES}, f, indent=2)
        
    # Datasets
    print("Loading datasets...")
    train_dataset = WasteDataset(manifest_path, "train", is_train=True)
    val_dataset = WasteDataset(manifest_path, "validation", is_train=False)
    
    batch_size = 32 if device.type in ["cuda", "mps"] else 16
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)
    
    # Class weights for imbalance
    class_counts = [0] * 8
    for item in train_dataset.data:
        class_counts[item["class_idx"]] += 1
        
    total_train = sum(class_counts)
    class_weights = [total_train / (8 * c) if c > 0 else 0 for c in class_counts]
    class_weights_tensor = torch.FloatTensor(class_weights).to(device)
    
    print("\nClass weights based on training split:")
    for i, w in enumerate(class_weights):
        print(f"  {TARGET_CLASSES[i]}: count={class_counts[i]}, weight={w:.4f}")
        
    criterion = nn.CrossEntropyLoss(weight=class_weights_tensor)
    
    # Model
    model = get_model(num_classes=8).to(device)
    
    all_history = []
    best_val_f1 = 0.0
    
    # Stage 1
    print("\n=== STAGE 1: CLASSIFIER TRAINING ===")
    freeze_backbone(model)
    optimizer1 = optim.AdamW(model.classifier.parameters(), lr=1e-3, weight_decay=1e-4)
    hist1, best_val_f1 = train_stage(
        model, "classifier", 5, train_loader, val_loader, criterion, optimizer1, 
        device, artifacts_dir, 0, best_val_f1
    )
    all_history.extend(hist1)
    
    # Stage 2
    print("\n=== STAGE 2: FINE TUNING ===")
    # Load best so far before unfreezing
    if (artifacts_dir / "best_model.pt").exists():
        model.load_state_dict(torch.load(artifacts_dir / "best_model.pt", map_location=device, weights_only=True))
    unfreeze_feature_blocks(model, blocks_to_unfreeze=2)
    optimizer2 = optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=1e-4, weight_decay=1e-4)
    hist2, best_val_f1 = train_stage(
        model, "finetune", 3, train_loader, val_loader, criterion, optimizer2, 
        device, artifacts_dir, len(hist1), best_val_f1
    )
    all_history.extend(hist2)
    
    # Save History
    with open(artifacts_dir / "training_history.json", "w") as f:
        json.dump({"epochs": all_history}, f, indent=2)
        
    # Write metadata (placeholder for evaluate.py to fill the rest)
    metadata = {
        "model_name": "efficientnet_b0",
        "architecture": "EfficientNet-B0 + Linear Classifier",
        "pretrained_weights": "EfficientNet_B0_Weights.DEFAULT",
        "num_classes": 8,
        "classes": TARGET_CLASSES,
        "image_size": 224,
        "normalization": {
            "mean": [0.485, 0.456, 0.406],
            "std": [0.229, 0.224, 0.225]
        },
        "device_used": device.type,
        "seed": 42,
        "train_images": len(train_dataset),
        "validation_images": len(val_dataset),
        "optimizer": "AdamW",
        "learning_rates": [1e-3, 1e-4],
        "batch_size": batch_size,
        "epochs": len(all_history),
        "best_validation_macro_f1": best_val_f1,
        "training_timestamp": datetime.utcnow().isoformat()
    }
    
    with open(artifacts_dir / "model_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
        
    print("\nTraining complete!")

if __name__ == "__main__":
    main()
