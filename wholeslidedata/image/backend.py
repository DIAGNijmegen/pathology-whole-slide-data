from abc import abstractmethod
from typing import List, Tuple
from creationism.registration.factory import RegistrantFactory
import numpy as np

LOAD_OPENSLIDE_BACKEND = False
try:
    from openslide import OpenSlide

    LOAD_OPENSLIDE_BACKEND = True
except ImportError:
    pass

LOAD_ASAP_BACKEND = False
try:
    from multiresolutionimageinterface import (
        MultiResolutionImage,
        MultiResolutionImageReader,
    )

    LOAD_ASAP_BACKEND = True
except ImportError:
    pass

LOAD_PYVIPS_BACKEND = False
try:
    import pyvips
    LOAD_PYVIPS_BACKEND = True
except ImportError:
    pass


class UnsupportedVendorError(KeyError):
    def __init__(self, path, properties):

        super().__init__(
            f"Image: '{path}', with properties: {properties}, is not in part of the supported vendors"
        )

        self._path = path
        self._properties = properties

    def __reduce__(self):
        return (UnsupportedVendorError, (self._path, self._properties))


class InvalidSpacingError(ValueError):
    def __init__(self, path, spacing, spacings, margin):

        super().__init__(
            f"Image: '{path}', with available pixels spacings: {spacings}, does not contain a level corresponding to a pixel spacing of {spacing} +- {margin}"
        )

        self._path = path
        self._spacing = spacing
        self._spacings = spacings
        self._margin = margin

    def __reduce__(self):
        return (
            InvalidSpacingError,
            (self._path, self._spacing, self._spacings, self._margin),
        )


class ImageBackend(RegistrantFactory):
    """ Image backend abstract class
    """


class WholeSlideImageBackend(ImageBackend):
    def __init__(self, path):
        self._path = path

    @abstractmethod
    def _init_shapes(self) -> List[Tuple[int, int]]:
        """[summary]

        Returns:
            List[Tuple[int, int]]: [description]
        """

    @abstractmethod
    def _init_downsamplings(self) -> List[float]:
        """[summary]

        Returns:
            List[float]: [description]
        """

    @abstractmethod
    def _init_spacings(self, downsamplings: List) -> List[float]:
        """[summary]

        Args:
            downsamplings (List): [description]

        Returns:
            List[float]: [description]
        """

    @abstractmethod
    def close(self):
        """[summary]
        """

    @abstractmethod
    def get_patch(
        self,
        x,
        y,
        width,
        heigth,
        spacing: float,
        center: bool = True,
        relative: bool = False,
    ) -> np.ndarray:
        """ """


if LOAD_OPENSLIDE_BACKEND:

    @WholeSlideImageBackend.register(("openslide",))
    class OpenSlideWholeSlideImageBackend(OpenSlide, WholeSlideImageBackend):
        def __init__(self, path: str) -> None:
            OpenSlide.__init__(self, str(path))
            WholeSlideImageBackend.__init__(self, path)

        def get_patch(
            self,
            x: int,
            y: int,
            width: int,
            height: int,
            level: int
        ) -> np.ndarray:

            return np.array(
                super().read_region(
                    (int(x), int(y)), int(level), (int(width), int(height))
                )
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
                    unit = {"cm": 10000, "centimeter": 10000}[
                        self.properties["tiff.ResolutionUnit"]
                    ]
                    res = float(self.properties["tiff.XResolution"])
                    spacing = unit / res
                except KeyError as key_error:
                    raise UnsupportedVendorError(
                        self._path, self.properties
                    ) from key_error

            return [
                spacing * downsamplings[level]
                for level in range(super().level_count)
            ]

        def close(self):
            super().close()


if LOAD_ASAP_BACKEND:

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
            self,
            x: int,
            y: int,
            width: int,
            height: int,
            level: int
        ) -> np.ndarray:

            return np.array(
                super().getUCharPatch(
                    int(x), int(y), int(width), int(height), int(level)
                )
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
                self.getLevelDownsample(level)
                for level in range(self.getNumberOfLevels())
            ]

        def _init_spacings(self, downsamplings: List) -> List[float]:
            try:
                return [
                    self.getSpacing()[0] * downsampling
                    for downsampling in downsamplings
                ]
            except:
                raise InvalidSpacingError(self._path, 0, [], 0)
        
        def close(self):
            try:
                super().close()
            except AttributeError:
                pass

if LOAD_PYVIPS_BACKEND:

    @WholeSlideImageBackend.register(('pyvips', ))
    class PyVipsImageBackend(WholeSlideImageBackend):
        def __init__(self, path: str) -> None:
            WholeSlideImageBackend.__init__(self, path)
            self._images = []
            self._images.append(pyvips.Image.openslideload(str(path), level=0))
            self._level_count = int(self._images[0].get('openslide.level-count'))
            for level in range(1, self._level_count):
                self._images.append(pyvips.Image.openslideload(str(path), level=level))
            self._regions = [pyvips.Region.new(image) for image in self._images]
            self._dowsamplings = self._init_downsamplings()
  
            
        def get_patch(
            self,
            x: int,
            y: int,
            width: int,
            height: int,
            level: int
        ) -> np.ndarray:
            image = self._regions[level]
            ratio =  self._dowsamplings[level]
            return np.array(image.fetch(int(x//ratio), int(y//ratio), int(width), int(height))).reshape(int(height), int(width), -1)[:, :, :3]
        
        def _init_shapes(self) -> List[Tuple[int, int]]:
            shapes= []
            for idx, image in enumerate(self._images):
                shapes.append((image.get(f'openslide.level[{idx}].width'),image.get(f'openslide.level[{idx}].height')))
            
            return shapes
                
        def _init_downsamplings(self) -> List[float]:
            downsamplings = []
            for idx, image in enumerate(self._images):
                downsamplings.append(float(image.get(f'openslide.level[{idx}].downsample')))
            return downsamplings
        
        def _init_spacings(self, downsamplings) -> List[float]:
            spacing = None
            try:
                spacing = float(self._images[0].get("openslide.mpp-x"))
            except:
                try:
                    unit = {"cm": 10000, "centimeter": 10000}[
                        self._images[0].get("tiff.ResolutionUnit")
                    ]
                    res = float(self._images[0].get("tiff.XResolution"))
                    spacing = unit / res
                except KeyError as key_error:
                    raise UnsupportedVendorError(
                        self._path, self._images[0].get_fields()
                    ) from key_error

            return [
                spacing * downsamplings[level]
                for level in range(self._level_count)
            ]

        def close(self):
            pass