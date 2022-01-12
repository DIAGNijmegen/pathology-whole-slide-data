import numpy as np
from collections import UserDict, Iterable
import pprint
from wholeslidedata.labels import Labels

class SpacingTypeError(Exception):
    pass


class ShapeTypeError(Exception):
    pass


class ShapeMismatchError(Exception):
    pass


class Sample(np.ndarray):
    def __new__(
        cls,
        input_array,
        image_path,
        annotation_label_name,
        annotation_index,
        center_coordinate,
        pixel_spacing,
        info={},
    ):
        obj = np.asarray(input_array).view(cls)
        obj.image_path = image_path
        obj.annotation_label_name = annotation_label_name
        obj.annotation_index = annotation_index
        obj.center_coordinate = center_coordinate
        obj.pixel_spacing = pixel_spacing
        obj.info = info
        return obj

    def __array_finalize__(self, obj):

        if obj is None:
            return
        self.image_path = getattr(obj, "image_path", None)
        self.annotation_label_name = getattr(obj, "annotation_label_name", None)
        self.annotation_index = getattr(obj, "annotation_index", None)
        self.center_coordinate = getattr(obj, "center_coordinate", None)
        self.pixel_spacing = getattr(obj, "pixel_spacing", None)
        self.info = getattr(obj, "info", None)

    def __reduce__(self):
        pickled_state = super(Sample, self).__reduce__()
        new_state = pickled_state[2] + (
            self.image_path,
            self.annotation_label_name,
            self.annotation_index,
            self.center_coordinate,
            self.pixel_spacing,
            self.info,
        )
        return (pickled_state[0], pickled_state[1], new_state)

    def __setstate__(self, state):
        self.image_path = state[-6]  # Set the info attribute     
        self.annotation_label_name = state[-5]
        self.annotation_index = state[-4]
        self.center_coordinate = state[-3]
        self.pixel_spacing = state[-2]
        self.info = state[-1]
        super(Sample, self).__setstate__(state[0:-6])


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
            return self._y_shape
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
                f"Spacings :{self._spacing} with type: {type(self._spacing)} has not a valid type "
            )

        shapes = None

        shapes_is_iterable = isinstance(self._shape, Iterable)
        if shapes_is_iterable and all(isinstance(s, (int, float)) for s in self._shape):
            shapes = [self._shape]
        elif shapes_is_iterable and all(isinstance(s, Iterable) for s in self._shape):
            shapes = self._shape
        else:
            ShapeTypeError(
                f"Shapes :{self._shape} with type: {type(self._shape)} has not a valid type "
            )

        inputs = {}

        # # TODO python has zip strict argument maybe use that instead
        if len(spacings) != len(shapes):
            raise ShapeMismatchError(
                f"spacings {spacings} and shapes {shapes} does not have same lengts"
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


class Batch:
    def __init__(self, x_batch, y_batch):
        self.info = self._set_info(x_batch, y_batch)
        self._batch_data = (x_batch, y_batch)

    def update(self, batch_data):
        self._batch_data = batch_data

    @property
    def data(self):
        return self._batch_data

    def _set_info(self, x_batch, y_batch):
        info_ = {"x": [], "y": []}
        for key_index, batch in enumerate([x_batch, y_batch]):
            for sample in batch:
                for pixel_spacing, shapes in sample.items():
                    for shape, sample in shapes.items():
                        info_[list(info_.keys())[key_index]].append(
                            {
                                "image_path": sample.image_path,
                                "annotation_index": sample.annotation_index,
                                "annotation_label_name": sample.annotation_label_name,
                                "center_coordinate": sample.center_coordinate,
                                "pixel_spacing": pixel_spacing,
                                "shape": shape,
                            }
                        )
        return info_
