import pytest
from PIL import Image
import torch
import io
import time

from app.ai.model import ModelLoader
from app.ai.predictor import Predictor

def create_synthetic_image():
    # Synthetic RGB image
    img = Image.new('RGB', (224, 224), color='red')
    return img

def test_model_loads_successfully():
    model, device = ModelLoader.get_model()
    assert model is not None, "Model failed to load"
    assert ModelLoader.is_available(), "Model available flag should be true"
    
def test_model_is_eval_mode():
    model, _ = ModelLoader.get_model()
    assert not model.training, "Model should be in eval mode"
    
def test_predictor_mechanics():
    img = create_synthetic_image()
    
    t0 = time.time()
    response = Predictor.predict(img)
    t1 = time.time()
    
    # Second inference should be faster as model is already loaded
    t2 = time.time()
    response2 = Predictor.predict(img)
    t3 = time.time()
    
    print(f"\nFirst inference time: {t1-t0:.4f}s")
    print(f"Subsequent inference time: {t3-t2:.4f}s")
    
    assert response is not None
    assert len(response.predictions) == 3, "Should return top-3 predictions"
    
    # Confidences
    conf_sum = sum(p.confidence for p in response.predictions)
    assert 0 <= conf_sum <= 1.01, "Top-3 sum of confidence should be <= 1"
    
    for p in response.predictions:
        assert 0 <= p.confidence <= 1
        assert p.confidence_level in ["high", "medium", "low"]
        assert p.label in ["plastic", "paper", "cardboard", "glass", "metal", "organic", "e-waste", "other"]
        
    assert response.predictions[0].confidence >= response.predictions[1].confidence
    assert response.predictions[1].confidence >= response.predictions[2].confidence
