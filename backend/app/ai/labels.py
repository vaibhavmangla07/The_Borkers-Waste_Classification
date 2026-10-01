from torchvision import models

class LabelManager:
    _labels = None

    @classmethod
    def get_labels(cls) -> list[str]:
        """
        Get the list of class labels for the current pretrained model.
        These are ImageNet labels, NOT our final waste categories.
        """
        if cls._labels is None:
            weights = models.MobileNet_V3_Small_Weights.DEFAULT
            cls._labels = weights.meta["categories"]
        return cls._labels
