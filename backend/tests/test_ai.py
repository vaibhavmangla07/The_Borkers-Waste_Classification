import pytest
from PIL import Image
import torch
from app.ai.device import get_device
from app.ai.model import ModelLoader
from app.ai.preprocessing import ImagePreprocessor
from app.ai.labels import LabelManager
from app.ai.predictor import Predictor

@pytest.fixture(scope="module")
def sample_image():
    # Create a simple red 224x224 RGB image
    img = Image.new("RGB", (224, 224), color="red")
    return img

def test_device_detection():
    device = get_device()
    assert isinstance(device, torch.device)
    assert device.type in ["cuda", "mps", "cpu"]

def test_model_loading():
    model, device = ModelLoader.get_model()
    assert model is not None
    # Verify model is in eval mode
    assert not model.training

def test_preprocessing():
    transform = ImagePreprocessor.get_transform()
    assert transform is not None

def test_label_manager():
    labels = LabelManager.get_labels()
    assert isinstance(labels, list)
    assert len(labels) > 0

def test_predictor(sample_image):
    response = Predictor.predict(sample_image)
    
    assert response.device in ["cuda", "mps", "cpu"]
    assert len(response.predictions) == 3 # TOP_K is 3
    
    prev_confidence = 1.0
    for i, pred in enumerate(response.predictions):
        assert pred.rank == i + 1
        assert 0.0 <= pred.confidence <= 1.0
        assert pred.confidence <= prev_confidence # ordered by confidence
        prev_confidence = pred.confidence
        assert pred.confidence_level in ["high", "medium", "low"]
        assert isinstance(pred.label, str)
