import math
from typing import List, Union
import numpy as np
from shapely import geometry
from wholeslidedata.annotation.labels import Label


class UnsupportedGeometryType(ValueError):
    ...


class InvalidCoordinatesError(ValueError):
    ...


def _get_geometry(
    coordinates: Union[list, dict]
) -> Union[geometry.Point, geometry.Polygon]:
    holes = []
    if isinstance(coordinates, dict):
        holes = coordinates["holes"]
        coordinates = coordinates["coordinates"]
    if len(coordinates) <= 1:
        raise InvalidCoordinatesError(f"Coordinates {coordinates} are not valid.")
    if len(coordinates) == 2:
        return geometry.Point(coordinates)
    return geometry.Polygon(coordinates, holes)


class Annotation:
    @staticmethod
    def create(index, label, coordinates, **kwargs):
        geometry = _get_geometry(coordinates)
        label = Label.create(label)
        if geometry.type == "Point":
            return PointAnnotation(index, label, geometry, **kwargs)
        if geometry.type == "Polygon":
            return PolygonAnnotation(index, label, geometry, **kwargs)
        raise UnsupportedGeometryType(
            f"Geometry type: {geometry.type} is not supported"
        )

    def __init__(
        self,
        index: int,
        label: Label,
        geometry: Union[geometry.Point, geometry.Polygon],
        **kwargs,
    ):
        self._index = index
        self._label = label
        self._geometry = geometry
        self._overlapping_annotations = []
        self._kwargs = kwargs

        for key, value in self._kwargs.items():
            print(key, value)
            self.__setattr__(key, value)

    @property
    def index(self) -> int:
        return self._index

    @property
    def label(self) -> Label:
        return self._label

    @property
    def geometry(self) -> Label:
        return self._geometry

    @property
    def type(self):
        return self._geometry.type.lower()

    @property
    def coordinates(self) -> List[tuple]:
        """_summary_

        Returns:
            List[tuple]: _description_
        """

    @property
    def center(self):
        """_summary_

        Returns:
            _type_: _description_
        """

    @property
    def centroid(self):
        return tuple(map(round, self._geometry.centroid.xy))

    @property
    def bounds(self):
        return np.array(list(map(round, self._geometry.bounds)))

    @property
    def size(self):
        xmin, ymin, xmax, ymax = self._geometry.bounds
        return math.ceil(xmax - xmin), math.ceil(ymax - ymin)

    @property
    def area(self):
        return round(self._geometry.area)

    @property
    def base_coordinates(self):
        return self.coordinates - self.bounds[:2]

    @property
    def xy(self):
        return self._geometry.xy

    def todict(self):
        return dict(
            index=self.index,
            coordinates=self.coordinates.tolist(),
            label=self.label.todict(),
            **self._kwargs,
        )

    def __str__(self):
        return ",".join(map(str, list(self.todict().values())))

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return (
            self.type == other.type
            and self.index == other.index
            and self.coordinates == other.coordinates
            and self.label == other.label
        )


class PointAnnotation(Annotation):
    @property
    def coordinates(self) -> List[tuple]:
        return np.array(list(self._geometry.coords))

    @property
    def center(self):
        return tuple(self._geometry.coords[0])

    @property
    def holes(self):
        return []


class PolygonAnnotation(Annotation):
    @property
    def coordinates(self) -> List[tuple]:
        return np.array(list(self._geometry.exterior.coords))

    @property
    def center(self):
        xmin, ymin, xmax, ymax = self._geometry.bounds
        return round(xmin + (xmax - xmin) / 2), round(ymin + (ymax - ymin) / 2)

    @property
    def holes(self):
        return [np.array(interior.xy).T for interior in self._geometry.interiors]

    def iou(self, annotation: Annotation):
        polygon_intersection = self._geometry.intersection(annotation._geometry).area
        polygon_union = self.union(annotation._geometry).area
        return polygon_intersection / polygon_union

    def contains(self, annotation: Annotation):
        # use prep ?
        # check overlapping annotations because if within overlapping than it contains not
        return self._geometry.buffer(0).contains(annotation._geometry) and np.all(
            [
                not _annotation.buffer(0).contains(annotation)
                for _annotation in self._overlapping_annotations
                if not isinstance(_annotation, PointAnnotation)
            ]
        )

    def add_overlapping_annotations(self, overlap_annotations):
        self._overlapping_annotations.append(overlap_annotations)
