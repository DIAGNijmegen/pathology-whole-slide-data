from functools import lru_cache
import math
from typing import List, Union
import numpy as np
from shapely import geometry
from wholeslidedata.annotation.labels import Label
from shapely.affinity import translate
from shapely.prepared import prep
from shapely.ops import triangulate


class UnsupportedGeometryType(ValueError):
    ...


class InvalidCoordinatesError(ValueError):
    ...


def _get_geometry(
    coordinates: Union[list, dict]
) -> Union[geometry.Point, geometry.Polygon]:

    if isinstance(coordinates, (geometry.Point, geometry.Polygon)):
        return coordinates

    holes = []
    if isinstance(coordinates, dict):
        holes = coordinates["holes"]
        coordinates = coordinates["coordinates"]
    if len(coordinates) == 2:
        return geometry.Point(coordinates)
    if len(coordinates) == 1 and len(coordinates[0]) == 2:
        return geometry.Point(coordinates[0])
    if len(coordinates) <= 1:
        raise InvalidCoordinatesError(f"Coordinates {coordinates} are not valid.")
    
    return geometry.Polygon(coordinates, holes).simplify(2.0)


def _triangulate(simplified_geometry, prepped_geometry):
    triangles = triangulate(simplified_geometry)

    tmp = {tuple(triangle.centroid.coords[0]): triangle for triangle in triangles}
    triangle_points = [triangle.centroid for triangle in triangles]
    filtered_points = list(filter(prepped_geometry.contains, triangle_points))
    filtered_triangles = [tmp[tuple(p.coords[0])] for p in filtered_points]

    areas = []
    transforms = []
    for t in filtered_triangles:
        areas.append(t.area)
        (x0, y0), (x1, y1), (x2, y2) = t.exterior.coords[:3]
        transforms.append([x1 - x0, x2 - x0, y1 - y0, y2 - y0, x0, y0])

    return {
        "transforms": transforms,
        "areas": areas,
        "triangles": filtered_triangles,
    }


class Annotation:
    @staticmethod
    def create(index, label, coordinates, **kwargs):
        geometry = _get_geometry(coordinates)
        label = Label.create(label)
        if geometry.geom_type == "Point":
            return PointAnnotation(index, label, geometry, **kwargs)
        if geometry.geom_type == "Polygon":
            return PolygonAnnotation(index, label, geometry, **kwargs)
        raise UnsupportedGeometryType(
            f"Geometry type: {geometry.geom_type} is not supported"
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
        return self._geometry.geom_type.lower()

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
        return tuple(map(round, [a[0] for a in self._geometry.centroid.xy]))

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

    def translate(self, offset):
        return Annotation.create(
            self._index,
            self._label,
            translate(self._geometry, -offset[0], -offset[1]),
            **self._kwargs,
        )
    def scale(self, scaling):
        return Annotation.create(
            self._index,
            self._label,
            self.coordinates * scaling,
            **self._kwargs,
        )

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
            and np.all(self.coordinates == other.coordinates)
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

    @lru_cache
    def triangles(self, buffer=0, simplify=2.0):
        simplified_geometry = self._geometry.buffer(buffer).simplify(simplify)
        prepped_geometry = prep(simplified_geometry)
        return _triangulate(simplified_geometry, prepped_geometry)
