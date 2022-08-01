from typing import List, Tuple

import numpy as np
from multiresolutionimageinterface import (
    MultiResolutionImage,
    MultiResolutionImageReader,
)
from wholeslidedata.image.backend import InvalidSpacingError, WholeSlideImageBackend


@WholeSlideImageBackend.register(("asap",))
class AsapWholeSlideImageBackend(MultiResolutionImage, WholeSlideImageBackend):
    def __init__(self, path: str) -> None:
        image = MultiResolutionImageReader().open(str(path))
        if image is None:
            raise ValueError(f"cant open image {path}")
        self.__dict__.update(image.__dict__)
        self.setCacheSize(0)
        WholeSlideImageBackend.__init__(self, path)

    def get_patch(
            self, x: int, y: int, width: int, height: int, level: int
    ) -> np.ndarray:

        return np.array(
            super().getUCharPatch(int(x), int(y), int(width), int(height), int(level))
        )

    def _init_shapes(self) -> List[Tuple]:
        try:
            return [
                tuple(self.getLevelDimensions(level))
                for level in range(self.getNumberOfLevels())
            ]
        except:
            raise ValueError("shape en level errors")

    def _init_downsamplings(self) -> List[float]:
        return [
            self.getLevelDownsample(level) for level in range(self.getNumberOfLevels())
        ]

    def _init_spacings(self, downsamplings: List) -> List[float]:
        try:
            return [
                self.getSpacing()[0] * downsampling for downsampling in downsamplings
            ]
        except:
            raise InvalidSpacingError(self._path, 0, [], 0)

    def close(self):
        try:
            super().close()
        except AttributeError:
            pass
