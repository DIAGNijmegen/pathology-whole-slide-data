import warnings

from pathlib import Path
from typing import List, Tuple, Union
from wholeslidedata.image.utils import take_closest_level
from wholeslidedata.image.backend import WholeSlideImageBackend
from wholeslidedata.extensions import WholeSlideImageExtension
from wholeslidedata.annotation.structures import Annotation
import numpy as np


class WholeSlideImage:
    SPACING_MARGIN = 0.3

    def __init__(
        self,
        path: Union[Path, str],
        backend: Union[WholeSlideImageBackend, str] = "openslide",
    ) -> None:

        """ WholeSlideImage that can open en sample from whole slide images

        Args:
            path (Union[Path, str]): path to whole slide image file
            backend (Union[WholeSlideImageBackend, str], optional): image backend that opens and extracts regions from the whole slide image. Defaults to 'openslide'.
        """

        self._path = Path(path)
        if not self._path.exists():
            raise ValueError(f'path {self._path} does not exists.')
        self._backend = WholeSlideImageBackend.create(backend, path=self._path)
        self._extension = WholeSlideImageExtension.create(self._path.suffix)

        self._shapes = self._backend._init_shapes()
        self._downsamplings = self._backend._init_downsamplings()
        self._spacings = self._backend._init_spacings(self._downsamplings)

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.close()

    def close(self):
        self._backend.close()

    @property
    def path(self) -> Path:
        return self._path

    @property
    def extension(self) -> WholeSlideImageExtension:
        return self._extension

    @property
    def spacings(self) -> List[float]:
        return self._spacings

    @property
    def shapes(self) -> List[Tuple[int, int]]:
        return self._shapes

    @property
    def downsamplings(self) -> List[float]:
        return self._downsamplings

    @property
    def level_count(self) -> int:
        return len(self.spacings)

    def get_downsampling_from_level(self, level: int) -> float:
        return self.downsamplings[level]

    def get_level_from_spacing(self, spacing: float) -> int:
        closest_level = take_closest_level(self._spacings, spacing)
        spacing_margin = spacing * WholeSlideImage.SPACING_MARGIN

        if abs(self.spacings[closest_level] - spacing) > spacing_margin:
            warnings.warn(
                f"spacing {spacing} outside margin (0.3%) for {self._spacings}, returning closest spacing: {self._spacings[closest_level]}"
            )

        return closest_level

    def get_real_spacing(self, spacing):
        level = self.get_level_from_spacing(spacing)
        return self._spacings[level]

    def get_slide(self, spacing):
        level = self.get_level_from_spacing(spacing)
        shape = self.shapes[level]
        return self.get_patch(0, 0, *shape, spacing, center=False)

    def get_annotation(self, annotation: Annotation, spacing: float, margin: int=0):
        scaling = self._spacings[0] / self.get_real_spacing(spacing)
        size = np.array(annotation.size) + margin
        return self.get_patch(
            *np.array(annotation.center),
            *np.array(size) * scaling,
            spacing=spacing,
        )

    def get_downsampling_from_spacing(self, spacing: float) -> float:
        level = self.get_level_from_spacing(spacing)
        return self.get_downsampling_from_level(level)

    def get_patch(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        spacing: float,
        center: bool = True,
        relative: bool = False,
    ) -> np.ndarray:

        """ Extracts a patch/region from the wholeslideimage

        Args:
            x (int): x value
            y (int): y value
            width (int): width of region
            height (int): height of region
            spacing (float): spacing/resolution of the patch
            center (bool, optional): if x,y values are centres or top left coordinated. Defaults to True.
            relative (bool, optional): if x,y values are a reference to the dimensions of the specified spacing. Defaults to False.

        Returns:
            np.ndarray: numpy patch
        """


        if relative and type(relative) in (float, int):
            rel_downsampling = int(self.get_downsampling_from_spacing(relative))
        else:
            rel_downsampling = int(self.get_downsampling_from_spacing(spacing))
        downsampling = int(self.get_downsampling_from_spacing(spacing))

        level = self.get_level_from_spacing(spacing)

        if relative:
            x, y = x * rel_downsampling, y * rel_downsampling
        if center:
            x, y = x - downsampling * (width // 2), y - downsampling * (height // 2)

        return self._backend.get_patch(x, y, width, height, level)