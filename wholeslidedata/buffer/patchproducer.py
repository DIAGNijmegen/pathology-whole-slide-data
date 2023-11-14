from copy import copy
from pathlib import Path

import numpy as np
from concurrentbuffer.producer import Producer

from wholeslidedata.image.wholeslideimage import WholeSlideImage

class PatchProducer(Producer):
    def __init__(
        self,
        image_path: Path,
        mask_path: Path = None,
        backend="openslide",
        producer_hooks=(),
    ):
        self._image_path = image_path
        self._mask_path = mask_path
        self._backend = backend
        self._image = None
        self._mask = None
        self._hooks = producer_hooks

    def build(self):
        self._image = WholeSlideImage(self._image_path, backend=self._backend)
        if self._mask_path is not None:
            self._mask = WholeSlideImage(
                self._mask_path,
                backend=self._backend,
                auto_resample=True,
            )

    def create_data(self, message: dict) -> np.ndarray:
        patches = [] 
        masks = []
        for spacing in message["spacings"]:
            patch = np.array(self._image.get_patch(
                x=message["x"],
                y=message["y"],
                width=message["tile_shape"][1],
                height=message["tile_shape"][0],
                spacing=spacing,
                center=message["center"],
            ))
            patches.append(patch)

            mask = None
            if self._mask is not None:
                mask = self._mask.get_patch(
                    x=message["x"],
                    y=message["y"],
                    width=message["tile_shape"][1],
                    height=message["tile_shape"][0],
                    spacing=spacing,
                    center=message['center'],
                    relative=self._image.spacings[0],
                ).squeeze()

            for callback in self._hooks:
                patch, mask = callback(patch, mask)
            
            if mask is not None:
                masks.append(mask)

        if len(masks) > 0:
            return [patches], [masks]
        return [patches]
