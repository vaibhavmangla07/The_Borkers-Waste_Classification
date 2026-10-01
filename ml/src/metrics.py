import numpy as np

def calculate_metrics(y_true, y_pred, y_prob):
    # Number of classes
    num_classes = 8
    
    # Accuracy
    accuracy = np.mean(y_true == y_pred)
    
    # Top-3 Accuracy
    top3_acc = 0.0
    for i in range(len(y_true)):
        top3 = np.argsort(y_prob[i])[-3:]
        if y_true[i] in top3:
            top3_acc += 1
    top3_acc /= len(y_true)
    
    # Precision, Recall, F1 per class
    precisions = []
    recalls = []
    f1s = []
    
    for c in range(num_classes):
        tp = np.sum((y_pred == c) & (y_true == c))
        fp = np.sum((y_pred == c) & (y_true != c))
        fn = np.sum((y_pred != c) & (y_true == c))
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        
        precisions.append(precision)
        recalls.append(recall)
        f1s.append(f1)
        
    macro_precision = np.mean(precisions)
    macro_recall = np.mean(recalls)
    macro_f1 = np.mean(f1s)
    
    return {
        "accuracy": float(accuracy),
        "top3_accuracy": float(top3_acc),
        "macro_precision": float(macro_precision),
        "macro_recall": float(macro_recall),
        "macro_f1": float(macro_f1),
        "per_class": {
            "precision": [float(p) for p in precisions],
            "recall": [float(r) for r in recalls],
            "f1": [float(f) for f in f1s]
        }
    }
