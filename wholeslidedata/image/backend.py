from abc import abstractmethod
from typing import List, Tuple
from creationism.registration.factory import RegistrantFactory
import numpy as np

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
        ...