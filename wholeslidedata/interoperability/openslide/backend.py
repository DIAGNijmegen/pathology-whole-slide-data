from typing import List, Tuple

import numpy as np
from wholeslidedata.image.backend import UnsupportedVendorError, WholeSlideImageBackend

from openslide import OpenSlide


class OpenSlideWholeSlideImageBackend(OpenSlide, WholeSlideImageBackend):
    def __init__(self, path: str) -> None:
        OpenSlide.__init__(self, str(path))
        WholeSlideImageBackend.__init__(self, path)
        try:
            from openslide import OpenSlideCache
            self.set_cache(OpenSlideCache(0))
        except:
            pass

    def get_patch(
        self, x: int, y: int, width: int, height: int, level: int
    ) -> np.ndarray:

        return np.array(
            super().read_region((int(x), int(y)), int(level), (int(width), int(height)))
        )[:, :, :3]

    def _init_shapes(self) -> List[Tuple[int, int]]:
        return self.level_dimensions

    def _init_downsamplings(self) -> List[float]:
        return self.level_downsamples

    def _init_spacings(self, downsamplings) -> List[float]:
        spacing = None
        try:
            spacing = float(self.properties["openslide.mpp-x"])
        except KeyError as key_error:
            try:
                unit = {
                    "cm": 10000, 
                    "centimeter": 10000, 
                    "inch": 25400, 
                    "inches": 25400  # 1 inch = 25400 micrometers
                }[self.properties["tiff.ResolutionUnit"]]
                res = float(self.properties["tiff.XResolution"])
                spacing = unit / res
            except KeyError as key_error:
                raise UnsupportedVendorError(self._path, self.properties) from key_error

        return [spacing * downsamplings[level] for level in range(super().level_count)]

    def close(self):
        super().close()
