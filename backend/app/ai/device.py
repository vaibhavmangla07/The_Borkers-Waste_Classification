import torch
import logging

logger = logging.getLogger(__name__)

def get_device() -> torch.device:
    """
    Detect and return the best available PyTorch device.
    Priority: CUDA -> Apple MPS -> CPU
    """
    if torch.cuda.is_available():
        logger.info("Using CUDA device.")
        return torch.device("cuda")
    
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        logger.info("Using Apple MPS device.")
        return torch.device("mps")
    
    logger.info("Using CPU device.")
    return torch.device("cpu")
