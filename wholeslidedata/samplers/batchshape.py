import numpy as np
from collections.abc import Iterable
from collections import UserDict
import pprint

class SpacingTypeError(Exception):
    pass


class ShapeTypeError(Exception):
    pass


class ShapeMismatchError(Exception):
    pass


class BatchShape(UserDict):
    def __init__(self, batch_size, spacing=None, shape=None, y_shape=None, labels=None):
        super().__init__(set())
        self._batch_size = batch_size
        self._spacing = spacing
        self._shape = shape
        self._y_shape = y_shape
        self._labels = labels
        self.data = self._set_inputs()

    @property
    def batch_size(self):
        return self._batch_size

    @property
    def shape(self):
        return tuple(self._shape)

    @property
    def y_shape(self):
        if self._labels is not None:
            count = len(self._labels)
            if 0 in self._labels.values:
                count = len(self._labels) - 1
            return tuple(self._shape[:2]+[count])
        if self._y_shape is None:
            return tuple(np.array(self.shape)[..., :2].tolist())
        return tuple(self._y_shape)

    @property
    def spacing(self):
        return list(self.data.keys())[0]

    def _set_inputs(self):
        spacings = None
        if isinstance(self._spacing, (int, float)):
            spacings = [self._spacing]
    
        elif isinstance(self._spacing, Iterable):
            spacings = self._spacing
        else:
            raise SpacingTypeError(
                f"Spacings :{self._spacing} with type: {type(self._spacing)} has invalid type "
            )

        shapes = None
        shapes_is_iterable = isinstance(self._shape, Iterable)
        if shapes_is_iterable and all(isinstance(s, (int, float)) for s in self._shape):
            shapes = [self._shape]
        elif shapes_is_iterable and all(isinstance(s, Iterable) for s in self._shape):
            shapes = self._shape
        else:
            raise ShapeTypeError(
                f"Shapes :{self._shape} with type: {type(self._shape)} has invalid type "
            )

        inputs = {}
        
        if len(spacings) != len(shapes):
            raise ShapeMismatchError(
                f"spacings {spacings} and shapes {shapes} do not have same lengths"
            )

        for spacing, shape in zip(spacings, shapes):
            inputs.setdefault(spacing, []).append(shape)

        return inputs

    def __str__(self):
        return pprint.pformat(
            {
                "object": self,
                "batch_size": self._batch_size,
                "x_shape": self.data,
                "y_shape": self._y_shape,
            }
        )

