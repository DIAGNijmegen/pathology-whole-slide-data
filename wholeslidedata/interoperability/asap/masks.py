from enum import Enum, auto

class MaskType(Enum):
    """Different mask types
    
    The PREDICTION type is for writing masks with prediction values, range=(0, num_classes)
    The HEATMAP type is for writing masks with heatmap values, range=(0, 255)
    """

    
    PREDICTION = auto()    
    HEATMAP = auto()