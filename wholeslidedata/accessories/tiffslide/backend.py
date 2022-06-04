import warnings
from typing import Dict, List, Optional, Tuple

import numpy as np
from wholeslidedata.image.backend import UnsupportedVendorError, WholeSlideImageBackend

warnings.filterwarnings("ignore", ".*aliasing tiffslide.TiffSlide.*")
from tiffslide import OpenSlide


@WholeSlideImageBackend.register(("tiffslide",))
class OpenSlideWholeSlideImageBackend(OpenSlide, WholeSlideImageBackend):
    def __init__(self, path: str, storage_options: Optional[Dict] = None) -> None:
        if storage_options is None:
            storage_options = {"anon": True}

        OpenSlide.__init__(self, str(path), storage_options=storage_options)
        WholeSlideImageBackend.__init__(self, path)

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
            spacing = float(self.properties["tiffslide.mpp-x"])
        except KeyError as key_error:
            try:
                unit = {"cm": 10000, "centimeter": 10000, "CENTIMETER": 10000}[
                    self.properties["tiff.ResolutionUnit"]
                ]
                res = float(self.properties["tiff.XResolution"])
                spacing = unit / res
            except KeyError as key_error:
                raise UnsupportedVendorError(self._path, self.properties) from key_error

        return [spacing * downsamplings[level] for level in range(super().level_count)]

    def close(self):
        super().close()
