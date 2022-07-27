from typing import List, Tuple

import numpy as np
from wholeslidedata.image.backend import UnsupportedVendorError, WholeSlideImageBackend
from cucim import CuImage

class _MixedMeta(type(WholeSlideImageBackend), type(CuImage)):
    pass

@WholeSlideImageBackend.register(("cucim",))
class CucimWholeSlideImageBackend(CuImage, WholeSlideImageBackend, metaclass=_MixedMeta):
    def __init__(self, path: str) -> None:
        CuImage.__init__(self, path)
        WholeSlideImageBackend.__init__(self, path)

    def get_patch(
        self, x: int, y: int, width: int, height: int, level: int
    ) -> np.ndarray:

        return np.array(
           super().read_region((int(x), int(y)), (int(width), int(height)), int(level))
        )[:, :, :3]

    def _init_shapes(self) -> List[Tuple[int, int]]:
        return super().metadata['cucim']['resolutions']['level_dimensions']

    def _init_downsamplings(self) -> List[float]:
        return  super().metadata['cucim']['resolutions']['level_downsamples']

    def _init_spacings(self, downsamplings) -> List[float]:
        spacing = super().spacing()[0]
        return [spacing * downsamplings[level] for level in range(super().metadata['cucim']['resolutions']['level_count'])]

    def close(self):
        super().close()
