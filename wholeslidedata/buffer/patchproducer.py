from re import L
from concurrentbuffer.producer import Producer
from pathlib import Path
from wholeslidedata.image.wholeslideimage import WholeSlideImage
import numpy as np
import cv2


class ScalingPatchHook:
    def __init__(self, scaling):
        self._scaling = scaling

    def __call__(self, patch):
        return cv2.resize(
            patch.squeeze().astype("uint8"),
            (
                int(patch.shape[0] * self._scaling),
                int(patch.shape[1] * self._scaling),
                patch.shape[2],
            ),
        )


class PatchProducer(Producer):
    def __init__(
        self,
        image_path: Path,
        tile_shape=(512, 512, 3),
        backend="openslide",
        producer_hooks=(),
        **kwargs
    ):
        self._image_path = image_path
        self._backend = backend
        self._image = None
        self._hooks = producer_hooks
        self._shapes = ((1, *tile_shape),)

    @property
    def shapes(self):
        return self._shapes

    def build(self):
        self._image = WholeSlideImage(self._image_path, backend=self._backend)

    def create_data(self, message: dict) -> np.ndarray:
        patch = self._image.get_patch(
            x=message["x"],
            y=message["y"],
            width=message["tile_shape"][1],
            height=message["tile_shape"][0],
            spacing=message["spacing"],
            center=False,
        )
        for hook in self._hooks:
            patch = hook(patch)

        return np.array([patch])