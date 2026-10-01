# EcoVision AI — AI Quality Report

## Model
EfficientNet-B0

## Dataset
15,496 usable images

## Categories
8

## Official Test Metrics

| Metric | Result |
|---|---:|
| Accuracy | 0.9250 |
| Macro Precision | 0.8697 |
| Macro Recall | 0.9071 |
| Macro F1 | 0.8854 |
| Weighted F1 | 0.9265 |
| Top-3 Accuracy | 0.9910 |

## Per-Class Metrics

| Category | Precision | Recall | F1 |
|---|---:|---:|---:|
| plastic | 0.7609 | 0.8077 | 0.7836 |
| paper | 0.9296 | 0.8354 | 0.8800 |
| cardboard | 0.9173 | 0.9037 | 0.9104 |
| glass | 0.9041 | 0.8800 | 0.8919 |
| metal | 0.7020 | 0.9138 | 0.7940 |
| organic | 0.8795 | 0.9799 | 0.9270 |
| e-waste | 0.8704 | 0.9860 | 0.9246 |
| other | 0.9939 | 0.9500 | 0.9715 |

## Confidence Analysis

We measured the model's confidence distribution over the test set:

- **Average confidence for correct predictions:** 0.9486
- **Average confidence for incorrect predictions:** 0.6851

**Accuracy by Confidence Bucket:**
- `0.00–0.39`: 37.5% accuracy (24 predictions)
- `0.40–0.59`: 59.5% accuracy (116 predictions)
- `0.60–0.79`: 67.1% accuracy (158 predictions)
- `0.80–0.89`: 81.8% accuracy (165 predictions)
- `0.90–1.00`: 98.3% accuracy (1869 predictions)

This analysis shows that the model is well-calibrated, with high confidence generally corresponding to high accuracy.

## Confusion Analysis

Based on the official classification report and confusion matrix:

1. **Strongest Categories:** `other` (F1: 0.9715, Precision: 0.9939). Due to its large representation in the dataset, the model correctly identifies this broad category very reliably. `organic` and `e-waste` also demonstrated exceptional recall (>0.97), meaning they are rarely missed.
2. **Weakest Categories:** `plastic` (F1: 0.7836) and `metal` (F1: 0.7940). 
3. **Common Confusions:**
   - `metal` suffers from very low precision (0.7020) but high recall (0.9138). This indicates the model over-predicts metal (frequently confusing other shiny/metallic items for metal waste).
   - `plastic` suffers from both lower precision and lower recall, indicating a broader class of confusion, likely with glass and metal due to specular reflections or transparency.

## Low Confidence Handling

The backend preserves three tiers of confidence:
- **HIGH:** >= 0.80
- **MEDIUM:** >= 0.60 and < 0.80
- **LOW:** < 0.60

When the confidence falls below 0.60, the system clearly communicates that the classification is uncertain. The existing 8 categories are strictly maintained (no fabricated "unknown" category is added). We still return the top prediction, but frontend consumers must handle the "LOW" confidence level explicitly to warn the user.

## Known Limitations

- **Dataset-dependent Performance:** The model is highly optimized for the 15,496 images in the `garbage_classification_dataset`. Performance in the wild depends heavily on how closely real-world images match the training distribution.
- **Softmax Confidence is NOT Probability of Correctness:** The model produces softmax probabilities that sum to 1 across the 8 known classes. High confidence (e.g. 0.99) does not guarantee correctness, but rather signifies a strong activation relative to other classes. 
- **Out-of-Domain Images:** Because EfficientNet-B0 always distributes 100% probability across its 8 learned classes, providing an image of a dog or a car will force it to predict one of the waste categories. **LOW confidence ≠ guaranteed non-waste**, and the system cannot perfectly reject arbitrary non-waste images without retraining on an out-of-distribution rejection class.
- **Class Imbalance:** `other` makes up ~52% of the dataset, which inherently skews the global accuracy higher than the model's performance on rare classes like `metal` or `cardboard`.
- **Visually Similar Categories:** As noted in the confusion analysis, specular materials like plastic and glass, or metallic items vs metal waste, introduce natural overlap that the classifier struggles to perfectly separate.

## API Validation

Real-image testing was conducted against `POST /api/classify`:
- The integration successfully returns `model_name="efficientnet_b0"`.
- It reliably surfaces top-3 predictions (with strict descending ranks 1, 2, 3 and strictly descending confidences).
- Disposal guidance correctly resolves for the top-1 prediction.
- Identical images yield deterministic top-1 and top-3 results.
- End-to-end database persistence captures the exact categories and confidences produced by the PyTorch model without applying legacy mock label mapping.
