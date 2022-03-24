import random
from typing import Tuple

import albumentations as A
import numpy as np

from wholeslidedata.accessories.albumentations import custom
from wholeslidedata.samplers.callbacks import BatchCallback


class AlbumentationsBase(BatchCallback):

    def __init__(self, custom_callbacks=None):
        super(AlbumentationsBase, self).__init__()
        if custom_callbacks:
            for cb in custom_callbacks:
                setattr(A, cb, getattr(custom, cb))


class AlbumentationsDetectionAugmentationsCallback(AlbumentationsBase):
    def __init__(self, augmentations, custom_callbacks=None):
        random.seed()
        super(AlbumentationsDetectionAugmentationsCallback, self).__init__(custom_callbacks)
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


class AlbumentationsAugmentationsCallback(AlbumentationsBase):

    def __init__(self, augmentations, custom_callbacks=None):
        random.seed()
        super(AlbumentationsAugmentationsCallback, self).__init__(custom_callbacks)
        self.augmentations = augmentations

    def __call__(
            self, x_batch: np.ndarray, y_batch: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        _type_x, _type_y = type(x_batch), type(y_batch)
        x_batch, y_batch = np.array(x_batch), np.array(y_batch)

        x_transformed, y_transformed = np.zeros(x_batch.shape), np.zeros(y_batch.shape)
        for batch_index in range(x_batch.shape[0]):
            if x_batch.ndim == 5:
                to_be_augmented = {"image": x_batch[batch_index][0], "mask": y_batch[batch_index][0]}
                additional_targets = {}
                for dim in range(1, x_batch.shape[1]):
                    additional_targets.update({f"image{dim}": "image", f"mask{dim}": "mask"})
                    to_be_augmented.update(
                        {f"image{dim}": x_batch[batch_index][dim], f"mask{dim}": y_batch[batch_index][dim]})
            else:
                additional_targets = None
                to_be_augmented = {"image": x_batch[batch_index], "mask": y_batch[batch_index]}

            self._augmentations = A.Compose(
                [getattr(A, class_name)(**params) for augmentation in self.augmentations for class_name, params in
                 augmentation.items()], additional_targets=additional_targets
            )
            augmented = self._augmentations(**to_be_augmented)
            if x_batch.ndim == 5:
                x_transformed[batch_index][0] = augmented[f"image"]
                y_transformed[batch_index][0] = augmented[f"mask"]
                for dim in range(1, x_batch.shape[1]):
                    x_transformed[batch_index][dim] = augmented[f"image{dim}"]
                    y_transformed[batch_index][dim] = augmented[f"mask{dim}"]
            else:
                x_transformed[batch_index] = augmented["image"]
                y_transformed[batch_index] = augmented["mask"]
        if _type_x != type(x_transformed):
            x_transformed = _type_x(x_transformed)
        if _type_y != type(y_transformed):
            y_transformed = _type_y(y_transformed)
        return x_transformed, y_transformed

    def reset(self):
        pass
