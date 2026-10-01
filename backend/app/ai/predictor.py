import torch
import torch.nn.functional as F
from PIL import Image
from fastapi import HTTPException

from app.ai.config import MODEL_NAME, MODEL_VERSION, TOP_K, get_confidence_level
from app.ai.model import ModelLoader
from app.ai.preprocessing import ImagePreprocessor
from app.ai.labels import LabelManager
from app.schemas.prediction import PredictionResponse, PredictionResult

class Predictor:
    @staticmethod
    def predict(image: Image.Image) -> PredictionResponse:
        """
        Run inference on the provided PIL Image.
        """
        # 1. Ensure model is loaded
        model, device = ModelLoader.get_model()
        
        if model is None:
            raise HTTPException(status_code=503, detail="AI model is currently unavailable")
        
        # 2. Preprocess image
        transform = ImagePreprocessor.get_transform()
        # Ensure image is RGB
        if image.mode != "RGB":
            image = image.convert("RGB")
            
        img_tensor = transform(image)
        # Add batch dimension: [1, C, H, W]
        img_tensor = img_tensor.unsqueeze(0).to(device)
        
        # 3. Inference
        with torch.inference_mode():
            output = model(img_tensor)
            
        # 4. Apply softmax to get probabilities
        probs = F.softmax(output[0], dim=0)
        
        # 5. Extract Top-K
        top_probs, top_idxs = torch.topk(probs, TOP_K)
        
        # 6. Map to labels
        labels = LabelManager.get_labels()
        
        predictions = []
        for i in range(TOP_K):
            prob = top_probs[i].item()
            idx = top_idxs[i].item()
            label_name = labels[idx] if idx < len(labels) else f"Unknown ({idx})"
            
            predictions.append(
                PredictionResult(
                    rank=i + 1,
                    label=label_name,
                    confidence=prob,
                    confidence_level=get_confidence_level(prob)
                )
            )
            
        return PredictionResponse(
            predictions=predictions,
            model_name=MODEL_NAME,
            model_version=MODEL_VERSION,
            device=str(device)
        )
