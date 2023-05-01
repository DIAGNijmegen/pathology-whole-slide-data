from pathlib import Path
from re import L

import cv2
import numpy as np
from concurrentbuffer.producer import Producer

from wholeslidedata.image.wholeslideimage import WholeSlideImage


class ScalingPatchHook:
    def __init__(self, scaling):
        self._scaling = scaling

    def __call__(self, patch, mask=None):
        resized_patch = cv2.resize(
            patch.squeeze().astype("uint8"),
            (
                int(patch.shape[0] * self._scaling),
                int(patch.shape[1] * self._scaling),
                patch.shape[2],
            ),
        )
        resized_mask = None
        if mask is not None:
            resized_mask = cv2.resize(
                resized_mask.squeeze().astype("uint8"),
                (
                    int(resized_mask.shape[0] * self._scaling),
                    int(resized_mask.shape[1] * self._scaling),
                ),
            )
        return resized_patch, resized_mask


class PatchProducer(Producer):
    def __init__(
        self,
        image_path: Path,
        mask_path: Path = None,
        tile_shape=(512, 512, 3),
        backend="openslide",
        producer_hooks=(),
        **kwargs
    ):
        self._image_path = image_path
        self._mask_path = mask_path
        self._backend = backend
        self._image = None
        self._mask = None
        self._hooks = producer_hooks
        if self._mask_path is not None:
            self._shapes = ((1, *tile_shape), (1, *tile_shape[:2]))
        else:
            self._shapes = ((1, *tile_shape),)

    @property
    def shapes(self):
        return self._shapes

    def build(self):
        self._image = WholeSlideImage(self._image_path, backend=self._backend)
        if self._mask_path is not None:
            self._mask = WholeSlideImage(
                self._mask_path,
                backend=self._backend,
                auto_resample=True,
            )

    def create_data(self, message: dict) -> np.ndarray:
        
        patch = self._image.get_patch(
            x=message["x"],
            y=message["y"],
            width=message["tile_shape"][1],
            height=message["tile_shape"][0],
            spacing=message["spacing"],
            center=False,
        )

        mask = None
        if self._mask is not None:
            mask = self._mask.get_patch(
                x=message["x"],
                y=message["y"],
                width=message["tile_shape"][1],
                height=message["tile_shape"][0],
                spacing=message["spacing"],
                center=False,
                relative=self._image.spacings[0],
            )

        for callback in self._hooks:
            patch, mask = callback(patch, mask)

        if mask is not None:
            print(mask.shape)
            return np.array([patch]), np.array([mask])

        return np.array([patch])