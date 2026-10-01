from torchvision import models

class ImagePreprocessor:
    _transform = None

    @classmethod
    def get_transform(cls):
        """
        Get the transforms associated with the pretrained model.
        """
        if cls._transform is None:
            # Must match the weights used in model.py
            weights = models.MobileNet_V3_Small_Weights.DEFAULT
            cls._transform = weights.transforms()
        return cls._transform
