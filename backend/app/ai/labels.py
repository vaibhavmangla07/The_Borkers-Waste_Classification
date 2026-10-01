import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class LabelManager:
    _labels = None

    @classmethod
    def get_labels(cls) -> list[str]:
        """
        Get the list of class labels for the current pretrained model.
        """
        if cls._labels is None:
            classes_path = Path(__file__).parent.parent.parent / "models" / "classes.json"
            try:
                with open(classes_path, 'r') as f:
                    cls._labels = json.load(f)["classes"]
            except Exception as e:
                logger.error(f"Error loading classes: {e}")
                cls._labels = []
        return cls._labels
