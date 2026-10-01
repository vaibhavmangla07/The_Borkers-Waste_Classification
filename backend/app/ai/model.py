import torch
from torchvision import models
import logging

from app.ai.device import get_device

logger = logging.getLogger(__name__)

class ModelLoader:
    _model = None
    _device = None

    @classmethod
    def get_model(cls):
        """
        Singleton pattern to load and return the model.
        """
        if cls._model is None:
            logger.info("Loading pretrained model...")
            try:
                # We use MobileNet_V3_Small_Weights.DEFAULT internally to get the best available weights
                weights = models.MobileNet_V3_Small_Weights.DEFAULT
                cls._model = models.mobilenet_v3_small(weights=weights)
                
                cls._device = get_device()
                cls._model = cls._model.to(cls._device)
                cls._model.eval()
                
                logger.info("Model loaded successfully.")
            except Exception as e:
                logger.error(f"Error loading model: {e}")
                raise RuntimeError("Failed to load AI model")
        return cls._model, cls._device
