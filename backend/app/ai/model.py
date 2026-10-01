import torch
import torch.nn as nn
from torchvision.models import efficientnet_b0
from pathlib import Path
import logging

from app.ai.device import get_device

logger = logging.getLogger(__name__)

class ModelLoader:
    _model = None
    _device = None
    _available = False

    @classmethod
    def get_model(cls):
        """
        Singleton pattern to load and return the model.
        """
        if cls._model is None:
            logger.info("Loading PyTorch model...")
            model_path = Path(__file__).parent.parent.parent / "models" / "best_model.pt"
            
            if not model_path.exists():
                logger.error(f"Model artifact not found at {model_path}")
                cls._available = False
                return None, None
                
            try:
                # Construct architecture matching the trained model
                model = efficientnet_b0(weights=None)
                num_ftrs = model.classifier[1].in_features
                # Match the improved classifier head used during training
                model.classifier = nn.Sequential(
                    nn.Dropout(p=0.3),
                    nn.Linear(num_ftrs, 256),
                    nn.ReLU(inplace=True),
                    nn.Dropout(p=0.2),
                    nn.Linear(256, 8),
                )
                
                cls._device = get_device()
                
                # Load weights
                state_dict = torch.load(model_path, map_location=cls._device, weights_only=True)
                model.load_state_dict(state_dict)
                
                cls._model = model.to(cls._device)
                cls._model.eval()
                cls._available = True
                
                logger.info("Model loaded successfully.")
            except Exception as e:
                logger.error(f"Error loading model: {e}")
                cls._available = False
                cls._model = None
                cls._device = None
                
        return cls._model, cls._device
        
    @classmethod
    def is_available(cls):
        if cls._model is None:
            # Attempt to load
            cls.get_model()
        return cls._available
