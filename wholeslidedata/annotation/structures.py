from pathlib import Path
from typing import List, Optional, Union
from dataclasses import dataclass
from shapely import geometry
import numpy as np
from creationism.registration.factory import RegistrantFactory
from wholeslidedata.labels import Labels, Label
import math 

@dataclass(frozen=True)
class AnnotationStructure:
    type: Union[str, type]
    index: int
    annotation_path: Union[Path, str]
    label: Union[str, Label]
    coordinates: list
    holes: Optional[list] = None

    def get_components(
        self,
        labels: Union[Labels, list, dict, set],
        rename_labels: Optional[Union[Labels, list, dict, set]] = None,
        scaling: float = 1.0,
    ):
        fields = {
            "index": self.index,
            "annotation_path": self.annotation_path,
            "label": self.label,
            "coordinates": self.coordinates,
        }
        self._set_holes(fields, scaling)

        fields["label"] = self._get_label(fields["label"], labels)
        fields["label"] = self._rename_label(fields["label"], rename_labels)
        fields["coordinates"] = self._scale_coordinates(fields["coordinates"], scaling)

        return fields

    def _set_holes(self, fields, scaling):
        if self.holes is None:
            return
        fields["holes"] = self.holes
        for idx, hole in enumerate(fields["holes"]):
            fields["holes"][idx] = self._scale_coordinates(hole, scaling)

    def _get_label(self, label, labels):
        if isinstance(label, Label):
            return label
        labels = Labels.create(labels)
        return labels.get_label_by_name(label)

    def _rename_label(self, label, rename_labels):
        if rename_labels is None:
            return label
        rename_labels = Labels.create(rename_labels)
        renamed_name = rename_labels.get_label_by_value(label.value).name
        return Label(renamed_name, label.value, color=label.color, weight=label.weight)

    def _scale_coordinates(self, coordinates, scaling):
        return np.array(coordinates) * scaling


class Annotation(RegistrantFactory):

    @classmethod
    def create(
        cls,
        annotation_structure: AnnotationStructure,
        labels: Union[Labels, list, dict, set],
        renamed_labels: Optional[Union[Labels, list, dict, set]] = None,
        scaling: float = 1.0,
    ):
        kwargs = annotation_structure.get_components(labels, renamed_labels, scaling)
        return super().create(registrant_name=annotation_structure.type, **kwargs)

    def __init__(self, index: int, annotation_path, label):
        self._index = index
        self._annotation_path = annotation_path
        self._label = label

    @property
    def index(self) -> int:
        return self._index

    @property
    def annotation_path(self) -> Path:
        return self._annotation_path

    @property
    def label(self) -> Label:
        return self._label

    def set_label(self, label):
        self._label = label


@Annotation.register(("polygon", "rectangle", "box", 'bounding-box'))
class Polygon(geometry.Polygon, Annotation):

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)


    def __init__(self, index, annotation_path, label, coordinates, holes=[]):
        Annotation.__init__(self, index, annotation_path, label)
        try:
            geometry.Polygon.__init__(self, coordinates, holes)
        except ValueError:
            raise ValueError(f'error parsing {annotation_path}')

        self._coordinates = np.array(self.exterior.xy).T 
        self._holes = holes
        self._overlapping_annotations = []

    def __reduce__(self):
        return (
            self.__class__,
            (
                self._index,
                self._annotation_path,
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
        return (self.coordinates - self.bounds[:2])

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

@Annotation.register(("point", "dot"))
class Point(geometry.Point, Annotation):

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)


    def __init__(self, index, annotation_path, label, coordinates, holes=None):
        geometry.Point.__init__(self, coordinates[0])
        Annotation.__init__(self, index, annotation_path, label)
        self._coordinates = coordinates

    def __reduce__(self):
        return (
            self.__class__,
            (
                self._index,
                self._annotation_path,
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