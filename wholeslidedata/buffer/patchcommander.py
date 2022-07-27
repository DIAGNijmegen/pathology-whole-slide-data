from abc import abstractmethod
from multiprocessing import Queue
from concurrentbuffer.commander import Commander

import numpy as np

from wholeslidedata.image.wholeslideimage import WholeSlideImage


def get_number_of_tiles(x_dims, y_dims, tile_shape, ratio):
    return len(range(0, y_dims, int(tile_shape[0]*ratio))) * len(
        range(0, x_dims, int(tile_shape[1]*ratio))
    )


class PatchCommander(Commander):
    def __init__(
        self,
        info_queue: Queue,
        image_path,
        spacing: float,
        backend="asap",
        tile_shape: int = (512, 512, 3),
        **kwargs,
    ):

        self._wsi = WholeSlideImage(image_path, backend=backend)
        self._spacing = spacing
        self._ratio = int(self._wsi.get_downsampling_from_spacing(spacing))
        self._x_dims, self._y_dims = self._wsi.shapes[0][:2]

        self._number_of_tiles = get_number_of_tiles(
            x_dims=self._x_dims,
            y_dims=self._y_dims,
            tile_shape=tile_shape,
            ratio=self._ratio
        )

        self._wsi.close()

        self._tile_shape = tile_shape
        self._info_queue = info_queue
        self._messages = []

    def __len__(self):
        return self._number_of_tiles

    @abstractmethod
    def get_patch_messages() -> list:
        ...

    def build(self):
        self.reset()

    def reset(self):
        self._messages = iter(self.get_patch_messages())

    def create_message(self) -> dict:
        try:
            return next(self._messages)
        except StopIteration:
            self.reset()
            return next(self._messages)


class SlidingPatchCommander(PatchCommander):
    def get_patch_messages(self):
        messages = []
        for row in range(0, self._y_dims, int(self._tile_shape[0] * self._ratio)):
            for col in range(0, self._x_dims, int(self._tile_shape[1] * self._ratio)):
                message = {
                    "x": col,
                    "y": row,
                    "tile_shape": self._tile_shape,
                    "spacing": self._spacing,
                }
                self._info_queue.put(message)
                messages.append(message)
        return messages


class RandomPatchCommander(PatchCommander):
    def __init__(
        self,
        info_queue: Queue,
        image_path,
        spacing: float,
        tile_shape: int = (512, 512, 3),
        seed: int = 123,
        number_of_tiles: int = 10,
        **kwargs,
    ):
        super().__init__(
            info_queue=info_queue,
            image_path=image_path,
            spacing=spacing,
            tile_shape=tile_shape,
        )
        self._number_of_tiles = number_of_tiles
        self._seed = seed
 
    def get_patch_messages(self):
        messages = []
        rows = self._rng.randint(0, self._y_dims - self._tile_shape[1]*self._ratio, self._number_of_tiles)
        cols = self._rng.randint(0, self._x_dims - self._tile_shape[0]*self._ratio,  self._number_of_tiles)
        for row, col in zip(rows, cols):
                message = {
                    "x": col,
                    "y": row,
                    "tile_shape": self._tile_shape,
                    "spacing": self._spacing,
                }
                self._info_queue.put(message)
                messages.append(message)
        return messages

    def reset(self):
        self._rng = np.random.RandomState(self._seed)
        super().reset()