from abc import abstractmethod
import math
from multiprocessing import Queue
from pathlib import Path
from concurrentbuffer.commander import Commander
from dataclasses import dataclass
import numpy as np

from wholeslidedata.image.wholeslideimage import WholeSlideImage
from wholeslidedata.samplers.utils import crop_data

@dataclass
class PatchConfiguration:
    patch_shape: tuple = (512, 512, 3)
    spacings: tuple = (0.5,)
    overlap: tuple = (0, 0)
    offset: tuple = (0, 0)
    center: bool = False
    write_shape: tuple = None # This can be used when you crop off (overlapping) borders of the patches, only patches with mask in the inner part will be sampled

class PatchCommander(Commander):
    def __init__(
        self,
        image_path,
        mask_path: Path = None,
        backend: str = "openslide",
        patch_configuration: PatchConfiguration = PatchConfiguration(),
    ):
        self._image_path = image_path
        self._mask_path = mask_path
        self._backend = backend
        self._patch_configuration = patch_configuration

        inputs = len(self._patch_configuration.spacings)
        shape = self._patch_configuration.patch_shape
        if self._mask_path is not None:
            self._shapes = ((1, inputs, *shape), (1, inputs, *shape[:2]))
        else:
            self._shapes = ((1, inputs, *shape),)
       
        wsi = WholeSlideImage(image_path, backend=backend)
        self._ratio = int(wsi.get_downsampling_from_spacing(self._patch_configuration.spacings[0]))
        self._x_dims, self._y_dims = wsi.shapes[0][:2]
        self._level_0_spacing = wsi.spacings[0]
        wsi.close()
        wsi = None
        del wsi

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
        
        wsm = None
        if self._mask_path is not None:
            wsm = WholeSlideImage(self._mask_path, backend=self._backend, auto_resample=True)

        x_min = self._patch_configuration.offset[0]
        y_min = self._patch_configuration.offset[1]
        x_max = self._x_dims + self._patch_configuration.offset[0] + self._patch_configuration.patch_shape[0] // 2 if self._patch_configuration.center else self._x_dims + self._patch_configuration.offset[0]
        y_max = self._y_dims + self._patch_configuration.offset[1] + self._patch_configuration.patch_shape[1] // 2 if self._patch_configuration.center else self._y_dims + self._patch_configuration.offset[1]

        # Add one extra patch on all sides to avoid missing out on patches in more complex patch configurations (e.g. with overlap and offset)
        if any(self._patch_configuration.offset) or any(self._patch_configuration.overlap):
            x_min = x_min - step_row
            y_min = y_min - step_col
            x_max = x_max + step_row
            y_max = y_max + step_col

        for row in range(y_min, y_max, step_row):
            for col in range(x_min, x_max, step_col):
                if wsm is not None:
                    mask = wsm.get_patch(
                        x=col,
                        y=row,
                        width=self._patch_configuration.patch_shape[1],
                        height=self._patch_configuration.patch_shape[0],
                        spacing=self._patch_configuration.spacings[0],
                        center=self._patch_configuration.center,
                        relative=self._level_0_spacing,
                    )

                    if self._patch_configuration.write_shape is not None:
                        mask = crop_data(mask, self._patch_configuration.write_shape)
                        if np.all(mask == 0):
                            continue
                    if np.all(mask == 0):
                        continue

                message = {
                    "x": col,
                    "y": row,
                    "tile_shape": self._patch_configuration.patch_shape,
                    "spacings": self._patch_configuration.spacings,
                    "center": self._patch_configuration.center
                }
                self._info_queue.put(message)
                messages.append(message)
        
        if wsm is not None:
            wsm.close()
            wsm = None
            del wsm

        return messages
