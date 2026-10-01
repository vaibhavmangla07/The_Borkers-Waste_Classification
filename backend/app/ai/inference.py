import json
import logging
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image, ImageOps
from torchvision import transforms
from torchvision.models import efficientnet_b0
from fastapi import HTTPException

from app.schemas.prediction import PredictionResponse, PredictionResult
from app.ai.device import get_device
from app.ai.config import MODEL_NAME, MODEL_VERSION, TOP_K, get_confidence_level

logger = logging.getLogger(__name__)

# Module-level variables for caching
_MODEL = None
_DEVICE = None
_LABELS = []
_TRANSFORM = None
_MODELS_DIR = Path(__file__).parent.parent.parent / "models"

def init_ai():
    """Load model, labels, and transforms into memory."""
    global _MODEL, _DEVICE, _LABELS, _TRANSFORM
    
    if _MODEL is not None:
        return  # Already initialized

    _DEVICE = get_device()
    
    # 1. Load Labels
    try:
        with open(_MODELS_DIR / "classes.json", 'r') as f:
            _LABELS = json.load(f)["classes"]
    except Exception as e:
        logger.error(f"Failed to load classes: {e}")
        _LABELS = ["plastic", "paper", "cardboard", "glass", "metal", "organic", "e-waste", "other"]

    # 2. Load Transforms (Hardcoded to what was trained for simplicity and correctness)
    _TRANSFORM = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    # 3. Load Model
    try:
        model = efficientnet_b0(weights=None)
        num_ftrs = model.classifier[1].in_features
        model.classifier = nn.Sequential(
            nn.Dropout(p=0.3),
            nn.Linear(num_ftrs, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.2),
            nn.Linear(256, 8),
        )
        
        state_dict = torch.load(_MODELS_DIR / "best_model.pt", map_location=_DEVICE, weights_only=True)
        model.load_state_dict(state_dict)
        model.to(_DEVICE)
        model.eval()
        
        # Optimize model via JIT trace for maximum efficiency
        example_input = torch.rand(1, 3, 224, 224).to(_DEVICE)
        with torch.no_grad():
            _MODEL = torch.jit.trace(model, example_input)
            
        logger.info("AI Model loaded and JIT traced successfully for maximum efficiency.")
    except Exception as e:
        logger.error(f"Failed to load AI model: {e}")
        _MODEL = None


def predict_image(image: Image.Image) -> PredictionResponse:
    """Run inference on a single image and return structured predictions."""
    init_ai()
    
    if _MODEL is None:
        raise HTTPException(status_code=503, detail="AI model is currently unavailable")

    # 1. Correct Image Orientation (EXIF)
    try:
        image = ImageOps.exif_transpose(image)
    except Exception:
        pass
        
    # 2. Handle PNG Transparency
    if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
        bg = Image.new("RGB", image.size, (255, 255, 255))
        try:
            bg.paste(image, mask=image.convert("RGBA").split()[3])
            image = bg
        except Exception:
            image = image.convert("RGB")
    elif image.mode != "RGB":
        image = image.convert("RGB")

    # 3. Preprocess
    img_tensor = _TRANSFORM(image).unsqueeze(0).to(_DEVICE)

    # 4. Inference
    with torch.inference_mode():
        output = _MODEL(img_tensor)
        probs = F.softmax(output[0], dim=0)
        
    # 5. Extract Top-K
    top_probs, top_idxs = torch.topk(probs, TOP_K)
    
    predictions = []
    for i in range(TOP_K):
        prob = top_probs[i].item()
        idx = top_idxs[i].item()
        label_name = _LABELS[idx] if idx < len(_LABELS) else f"Unknown ({idx})"
        
        predictions.append(PredictionResult(
            rank=i + 1,
            label=label_name,
            confidence=prob,
            confidence_level=get_confidence_level(prob)
        ))
        
    return PredictionResponse(
        predictions=predictions,
        model_name=MODEL_NAME,
        model_version=MODEL_VERSION,
        device=str(_DEVICE)
    )
