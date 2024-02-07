from typing import List
from shapely.geometry import Polygon, Point, box
from wholeslidedata.annotation.parser import (
    AnnotationParser,
    AnnotationType,
)
from wholeslidedata.annotation.labels import Label, Labels
from darwin.utils import parse_darwin_json


class DarwinPolygon:
    def __init__(self, polygon):
        self.geom = polygon
        self.hole = False
        self.holes = []


def parse_complex_polygon(annotation):
    polygons = []
    for path in annotation.data["paths"]:
        polygons.append(DarwinPolygon(Polygon([(p["x"], p["y"]) for p in path])))

    # naive even-odd rule
    sorted_polygons = sorted(polygons, key=lambda x: x.geom.area, reverse=True)
    for idx, my_polygon in enumerate(sorted_polygons):
        for outer_polygon in reversed(sorted_polygons[:idx]):
            contains = outer_polygon.geom.contains(my_polygon.geom)
            if contains and outer_polygon.hole:
                break
            if outer_polygon.hole:
                continue
            if contains:
                my_polygon.hole = True
                outer_polygon.holes.append(my_polygon.geom.exterior.coords)

    # create complex polygon with MultiPolygon
    polygons = [
        Polygon(my_polygon.geom.exterior.coords, my_polygon.holes)
        for my_polygon in sorted_polygons
        if not my_polygon.hole
    ]

    for polygon in polygons:
        yield polygon


class V7AnnotationParser(AnnotationParser):
    parse_to_shapely = {
        "keypoint": lambda annotation: [
            Point((annotation.data["x"], annotation.data["x"]))
        ],
        "polygon": lambda annotation: [
            Polygon([(p["x"], p["y"]) for p in annotation.data["path"]])
        ],
        "bounding_box": lambda annotation: [
            box(
                annotation.data["x"],
                annotation.data["y"],
                annotation.data["x"] + annotation.data["w"],
                annotation.data["y"] + annotation.data["h"],
            )
        ],
        "complex_polygon": lambda annotation: parse_complex_polygon(annotation),
    }

    @staticmethod
    def get_available_labels(opened_annotation: dict):
        return Labels.create(
            set([annotation.annotation_class.name for annotation in opened_annotation])
        )

    def _open_annotation(self, path):
        annotation = parse_darwin_json(path, None)
        if annotation is None:
            print("None for", path)
            return []
        return annotation.annotations

    def _parse(self, path) -> List[dict]:
        if not self._path_exists(path):
            raise FileNotFoundError(path)

        annotations = self._open_annotation(path)
        labels = self._get_labels(annotations)

        for annotation in annotations:
            label_name = annotation.annotation_class.name.lower()
            if label_name not in labels.names:
                continue
            label = labels.get_label_by_name(label_name)
            
            # set coordinates
            for polygon in self._get_polygons(
                annotation, annotation.annotation_class.annotation_type
            ):
                yield {
                    "coordinates": polygon,
                    "label": label.todict(),
                }

    def _get_polygons(self, annotation, type):
        for polygon in V7AnnotationParser.parse_to_shapely[type](annotation):
            yield polygon
