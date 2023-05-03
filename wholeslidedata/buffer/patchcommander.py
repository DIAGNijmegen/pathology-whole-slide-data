from abc import abstractmethod
from multiprocessing import Queue
from pathlib import Path
from concurrentbuffer.commander import Commander
from dataclasses import dataclass
import numpy as np

from wholeslidedata.image.wholeslideimage import WholeSlideImage


@dataclass
class PatchConfiguration:
    patch_shape: tuple = (512, 512, 3)
    spacing: float = 0.5
    overlap: tuple = (0, 0)
    offset: tuple = (0, 0)
    center: bool = False


class PatchCommander(Commander):
    def __init__(
        self,
        image_path,
        mask_path: Path = None,
        backend: str = "asap",
        patch_configuration: PatchConfiguration = PatchConfiguration(),
    ):
        self._image_path = image_path
        self._mask_path = mask_path
        self._backend = backend
        self._patch_configuration = patch_configuration

        if self._mask_path is not None:
            self._shapes = ((1, *self._patch_configuration.patch_shape), (1, *self._patch_configuration.patch_shape[:2]))
        else:
            self._shapes = ((1, *self._patch_configuration.patch_shape),)
       
        wsi = WholeSlideImage(image_path, backend=backend)
        self._ratio = int(wsi.get_downsampling_from_spacing(self._patch_configuration.spacing))
        self._x_dims, self._y_dims = wsi.shapes[0][:2]
        self._level_0_spacing = wsi.spacings[0]
        wsi.close()
       
        self._info_queue = Queue()
        self._n_messages = None
        self._messages = []
        self.reset()

    def __len__(self):
        return self._n_messages

    @property
    def shapes(self):
        return self._shapes

    @property
    def info_queue(self):
        return self._info_queue

    @abstractmethod
    def get_patch_messages() -> list:
        ...

    def reset(self):
        messages = self.get_patch_messages()
        self._n_messages = len(messages)
        self._messages = iter(messages)

    def create_message(self) -> dict:
        try:
            return next(self._messages)
        except StopIteration:
            self.reset()
            return next(self._messages)


class SlidingPatchCommander(PatchCommander):
    def get_patch_messages(self):
        messages = []
        step_row = int(self._patch_configuration.patch_shape[0] * self._ratio) - int(
            self._patch_configuration.overlap[0] * self._ratio
        )
        step_col = int(self._patch_configuration.patch_shape[1] * self._ratio) - int(
            self._patch_configuration.overlap[1] * self._ratio
        )
        for row in range(self._patch_configuration.offset[0], self._y_dims, step_row):
            for col in range(self._patch_configuration.offset[1], self._x_dims, step_col):
                if self._mask_path is not None:
                    self._mask = WholeSlideImage(self._mask_path, backend=self._backend, auto_resample=True)

                    mask = self._mask.get_patch(
                        x=col,
                        y=row,
                        width=self._patch_configuration.patch_shape[1],
                        height=self._patch_configuration.patch_shape[0],
                        spacing=self._patch_configuration.spacing,
                        center=self._patch_configuration.center,
                        relative=self._level_0_spacing,
                    )

                    if np.all(mask == 0):
                        continue

                message = {
                    "x": col,
                    "y": row,
                    "tile_shape": self._patch_configuration.patch_shape,
                    "spacing": self._patch_configuration.spacing,
                    "center": self._patch_configuration.center
                }
                self._info_queue.put(message)
                messages.append(message)
        return messages


# class RandomPatchCommander(Commander):
#     def get_patch_messages(self):
#         messages = []
#         rows = self._rng.randint(
#             0, self._y_dims - self._patch_shape[1] // self._ratio, self._number_of_tiles
#         )
#         cols = self._rng.randint(
#             0, self._x_dims - self._patch_shape[0] // self._ratio, self._number_of_tiles
#         )
#         for row, col in zip(rows, cols):
#             message = {
#                 "x": col,
#                 "y": row,
#                 "tile_shape": self._patch_shape,
#                 "spacing": self._spacing,
#             }
#             self._info_queue.put(message)
#             messages.append(message)
#         return messages

