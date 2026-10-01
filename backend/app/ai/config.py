import os

# Base AI configuration
MODEL_NAME = os.getenv("AI_MODEL_NAME", "efficientnet-b0")
MODEL_VERSION = os.getenv("AI_MODEL_VERSION", "waste-v1")
TOP_K = int(os.getenv("AI_TOP_K", "3"))

def get_confidence_level(confidence: float) -> str:
    """
    Categorize confidence into high, medium, low.
    """
    if confidence >= 0.80:
        return "high"
    elif confidence >= 0.60:
        return "medium"
    return "low"
