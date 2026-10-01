# EcoVision AI - Training Report

## Objective
Train a waste classification model mapping images to 8 application categories.

## Dataset & Split
- Total Train Images: 10844
- Total Validation Images: 2320
- Total Test Images: 2332
- 8 Categories: plastic, paper, cardboard, glass, metal, organic, e-waste, other

## Imbalance Handling
Weighted CrossEntropyLoss computed from training split distribution.

## Model
- Architecture: EfficientNet-B0 + Linear Classifier
- Pretrained Weights: EfficientNet_B0_Weights.DEFAULT
- Input Size: 224
- Device: mps
- Seed: 42

## Training
Stage 1 (Classifier): 5 epochs
Stage 2 (Fine-tuning): 3 epochs (Top 2 blocks unfreezed)
Best Validation Macro F1: 0.9055

## Test Performance
- Accuracy: 0.9250
- Top-3 Accuracy: 0.9910
- Macro F1: 0.8854

## Backend Integration
The model artifact is saved in `ml/artifacts/best_model.pt`. It's a raw state dict. The backend predictor will need to initialize an EfficientNet-B0 backbone with an 8-class linear classifier and load these weights. Classes mapping matches exactly with `ml/artifacts/classes.json`.
