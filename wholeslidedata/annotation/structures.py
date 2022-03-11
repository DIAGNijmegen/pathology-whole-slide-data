import math
import warnings
from typing import Optional, Union

import numpy as np
from creationism.registration.factory import RegistrantFactory
from shapely import geometry
from wholeslidedata.labels import Label

warnings.filterwarnings(
    "ignore",
    "Setting custom attributes on geometry objects is deprecated, and will raise an AttributeError in Shapely 2.0",
)


class Annotation(RegistrantFactory, geometry.base.BaseGeometry):
    @classmethod
    def create(cls, type: Union[str, type], *args, **kwargs):
        return super().create(registrant_name=type, *args, **kwargs)

    def __init__(self, label: Union[Label, dict], index: Optional[int] = None):
        self._label = Label.create(label)
        self._index = index

    @property
    def index(self) -> int:
        return self._index

    @property
    def label(self) -> Label:
        return self._label

    def set_label(self, label):
        self._label = label

    @property
    def type(self):
        return super().type.lower()


@Annotation.register(("point", "dot"))
class Point(geometry.Point, Annotation):
    def __init__(self, label, coordinates, index: Optional[int] = None):
        geometry.Point.__init__(self, coordinates)
        Annotation.__init__(self, label=label, index=index)
        self._coordinates = coordinates

    def __reduce__(self):
        return (
            self.__class__,
            (
                self._index,
                self._label,
                self._coordinates,
            ),
        )

    @property
    def coordinates(self):
        return np.array([self.x, self.y])

    @property
    def center(self):
        return self.x, self.y

    @property
    def centroid(self):
        return self.center

    @property
    def area(self):
        return 1


@Annotation.register(("polygon", "rectangle", "box", "bounding-box"))
class Polygon(geometry.Polygon, Annotation):
    def __init__(self, label, coordinates, holes=[], index: Optional[int] = None):
        geometry.Polygon.__init__(self, coordinates, holes=holes)
        Annotation.__init__(self, label=label, index=index)

        self._coordinates = np.array(self.exterior.xy).T
        self._holes = holes
        self._overlapping_annotations = []

    def __reduce__(self):
        return (
            self.__class__,
            (
                self._index,
                self._label,
                self._coordinates,
                self._holes,
            ),
        )

    @property
    def coordinates(self):
        return self._coordinates

    @property
    def holes(self):
        return [np.array(interior.xy).T for interior in self.interiors]

    @property
    def base_coordinates(self):
        return self.coordinates - self.bounds[:2]

    @property
    def bounds(self):
        x1, y1, x2, y2 = super().bounds
        return [int(x1), int(y1), int(x2), int(y2)]

    @property
    def size(self):
        xmin, ymin, xmax, ymax = super().bounds
        return math.ceil(xmax - xmin), math.ceil(ymax - ymin)

    @property
    def centroid(self):
        c = super().centroid
        x, y = c.xy
        return round(x[0]), round(y[0])

    @property
    def center(self):
        xmin, ymin, xmax, ymax = super().bounds
        return round(xmin + (xmax - xmin) / 2), round(ymin + (ymax - ymin) / 2)

    @property
    def overlapping_annotations(self):
        return self._overlapping_annotations

    @property
    def xy(self):
        return super().xy

    def iou(self, polygon):
        polygon_intersection = self.intersection(polygon).area
        polygon_union = self.union(polygon).area
        return polygon_intersection / polygon_union

    def contains(self, _annotation):
        # use prep ?
        # check overlapping annotations because if within overlapping than it contains not
        return super().buffer(0).contains(_annotation) and np.all(
            [
                not annotation.buffer(0).contains(_annotation)
                for annotation in self._overlapping_annotations
                if not isinstance(annotation, Point)
            ]
        )

    def add_overlapping_annotations(self, overlap_annotations):
        self._overlapping_annotations.extend(overlap_annotations)
