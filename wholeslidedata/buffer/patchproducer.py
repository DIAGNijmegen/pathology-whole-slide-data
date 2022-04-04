from concurrentbuffer.producer import Producer
from pathlib import Path
from wholeslidedata.image.wholeslideimage import WholeSlideImage
import numpy as np
import cv2


class PatchProducer(Producer):
    def __init__(self, image_path: Path, scaling=1, backend="openslide"):
        self._image_path = image_path
        self._scaling = scaling
        self._backend = backend
        self._image = None

    def build(self):
        self._image = WholeSlideImage(self._image_path, backend=self._backend)

    def create_data(self, message: dict) -> np.ndarray:
        patch = self._image.get_patch(
            x=message["x"],
            y=message["y"],
            width=message["tile_size"],
            height=message["tile_size"],
            spacing=message["spacing"],
            center=False,
        )

        p = cv2.resize(
            patch.squeeze().astype("uint8"),
            [
                int(message["tile_size"] * self._scaling),
                int(message["tile_size"] * self._scaling),
            ],
        )

        return np.array([p])