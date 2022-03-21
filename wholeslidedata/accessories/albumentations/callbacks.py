import random

import albumentations as A

from wholeslidedata.accessories.albumentations.custom import *
from wholeslidedata.samplers.callbacks import SampleCallback


class AlbumentationsDetectionAugmentationsCallback(SampleCallback):
    def __init__(self, augmentations):
        random.seed()
        super().__init__()
        self._augmentations = A.Compose(
            [
                getattr(A, class_name)(**params)
                for augmentation in augmentations
                for class_name, params in augmentation.items()
            ],
            bbox_params=A.BboxParams(format="pascal_voc"),
        )

    def __call__(
            self, x_patch: np.ndarray, y_patch: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        y_boxes = y_patch[~np.all(y_patch == 0, axis=-1)]
        augmented = self._augmentations(image=x_patch, bboxes=y_boxes)
        if y_boxes.size != 0:
            y_patch[~np.all(y_patch == 0, axis=-1)] = augmented["bboxes"]
        return augmented["image"], y_patch

    def reset(self):
        pass


class AlbumentationsAugmentationsCallback(SampleCallback):

    def __init__(self, augmentations, custom_callbacks):
        random.seed()
        super().__init__()
        for cb in custom_callbacks:
            setattr(A, cb, eval(cb))
        self._augmentations = A.Compose(
            [getattr(A, class_name)(**params) for augmentation in augmentations for class_name, params in
             augmentation.items()]
        )

    def __call__(
            self, x_patch: np.ndarray, y_patch: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        augmented = self._augmentations(image=x_patch, mask=y_patch)
        return augmented["image"], augmented["mask"]

    def reset(self):
        pass
