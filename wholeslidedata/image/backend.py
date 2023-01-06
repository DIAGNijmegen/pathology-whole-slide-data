from abc import abstractmethod
from typing import List, Tuple
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


class WholeSlideImageBackend:
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
        """[summary]"""

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