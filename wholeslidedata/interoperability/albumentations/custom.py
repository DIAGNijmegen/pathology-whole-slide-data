from typing import Dict, Any, Tuple

from albumentations import ImageOnlyTransform
from albumentations.augmentations import functional as F
import numpy as np


class InstanceNormalize(ImageOnlyTransform):
    """Normalization is applied by the formula: `img = (img - mean * max_pixel_value) / (std * max_pixel_value)`
    Args:
        axis (tuple, int, None): take mean and std along these axis.
        std  (float, list of float): std values
        max_pixel_value (float): maximum possible pixel value
    Targets:
        image
    Image types:
        uint8, float32
    """

    def __init__(
            self,
            axis=(0, 1),
            max_pixel_value=255.0,
            always_apply=False,
            p=1.0,
    ):
        super(InstanceNormalize, self).__init__(always_apply, p)
        self.axis = axis
        self.max_pixel_value = max_pixel_value

    def apply(self, image: np.ndarray, **params):
        mean = image.mean(axis=self.axis, keepdims=True)
        std = image.std(axis=self.axis, keepdims=True)
        return F.normalize(image, mean, std, self.max_pixel_value)

    def get_transform_init_args_names(self) -> Tuple[str, ...]:
        return "axis", "max_pixel_value"

    def get_params_dependent_on_targets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        pass
