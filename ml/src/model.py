import torch
import torch.nn as nn
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights

def get_model(num_classes=8):
    # Load pretrained model
    weights = EfficientNet_B0_Weights.DEFAULT
    model = efficientnet_b0(weights=weights)
    
    # Replace final classifier
    num_ftrs = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(num_ftrs, num_classes)
    
    return model

def freeze_backbone(model):
    for param in model.parameters():
        param.requires_grad = False
    for param in model.classifier.parameters():
        param.requires_grad = True

def unfreeze_feature_blocks(model, blocks_to_unfreeze=2):
    # Unfreeze the classifier just in case
    for param in model.classifier.parameters():
        param.requires_grad = True
        
    # EfficientNet has features (Sequential). Unfreeze the last few blocks.
    features = list(model.features.children())
    for block in features[-blocks_to_unfreeze:]:
        for param in block.parameters():
            param.requires_grad = True
