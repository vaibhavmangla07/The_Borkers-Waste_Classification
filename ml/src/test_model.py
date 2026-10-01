import torch
from dataset import TARGET_CLASSES
from model import get_model
from utils import get_device

def smoke_test():
    device = get_device()
    model = get_model(num_classes=8)
    model.load_state_dict(torch.load("ml/artifacts/best_model.pt", map_location=device, weights_only=True))
    model.to(device)
    model.eval()

    # Synthetic image input: [batch_size, channels, height, width]
    dummy_input = torch.randn(1, 3, 224, 224).to(device)
    
    with torch.no_grad():
        logits = model(dummy_input)
    
    # Shape check
    assert logits.shape == (1, 8), f"Expected shape (1, 8), got {logits.shape}"
    
    # Softmax and probabilities
    probs = torch.softmax(logits, dim=1)
    
    assert torch.isclose(probs.sum(), torch.tensor(1.0).to(device), atol=1e-5), "Probabilities do not sum to 1"
    
    # Top-3 predictions
    top_probs, top_indices = torch.topk(probs, 3, dim=1)
    
    print("\nSmoke Test Predictions:")
    for i in range(3):
        idx = top_indices[0][i].item()
        p = top_probs[0][i].item()
        print(f"{i+1}. {TARGET_CLASSES[idx]}: {p:.4f}")
        
    print("Smoke test passed successfully!")

if __name__ == "__main__":
    smoke_test()
