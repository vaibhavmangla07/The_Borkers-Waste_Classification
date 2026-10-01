from torchvision import transforms
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ImagePreprocessor:
    _transform = None

    @classmethod
    def get_transform(cls):
        """
        Get the transforms associated with the real PyTorch model.
        """
        if cls._transform is None:
            try:
                meta_path = Path(__file__).parent.parent.parent / "models" / "model_metadata.json"
                with open(meta_path, 'r') as f:
                    meta = json.load(f)
                
                mean = meta["normalization"]["mean"]
                std = meta["normalization"]["std"]
                size = meta["image_size"]
                
                cls._transform = transforms.Compose([
                    transforms.Resize(256),
                    transforms.CenterCrop(size),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=mean, std=std)
                ])
            except Exception as e:
                logger.error(f"Error loading transform config: {e}")
                # Fallback to standard ImageNet
                cls._transform = transforms.Compose([
                    transforms.Resize(256),
                    transforms.CenterCrop(224),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                ])
                
        return cls._transform
