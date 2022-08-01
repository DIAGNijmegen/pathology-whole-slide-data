import json
from typing import List

import cv2
import jsonschema
import numpy as np
from matplotlib import pyplot as plt
from scipy.ndimage.morphology import binary_dilation, binary_erosion, binary_fill_holes
from shapely import geometry
from shapely.strtree import STRtree
from wholeslidedata.annotation.parser import SCHEMA
from wholeslidedata.annotation.structures import Annotation, Point, Polygon
from wholeslidedata.labels import Labels


class GeometrySelector:
    def __init__(self, geometries: List[geometry.base.BaseGeometry]):
        self._geometries = geometries
        self._tree = STRtree(geometries)

    def select_annotations(
        self, center_x: int, center_y: int, width: int, height: int
    ) -> List[geometry.base.BaseGeometry]:

        """Selects annotations within specific region

        Args:
            center_x (int): x center of region
            center_y (int): y center of region
            width (int): width of region
            height (int): height of region

        Returns:
            List[geometry.base.BaseGeometry]: all geometries that overlap with specified region
        """

        box = geometry.box(
            center_x - width // 2,
            center_y - height // 2,
            center_x + width // 2,
            center_y + height // 2,
        )
        return self._tree.query(box)


def get_labels_in_annotations(annotations):
    return Labels(labels=[annotation.label for annotation in annotations])


def get_counts_in_annotations(annotations, labels=None):
    if labels is None:
        return len(annotations)
    return _counts_per_class(annotations, labels)


def get_pixels_in_annotations(annotations, labels=None):
    if labels is None:
        return int(sum([annotation.area for annotation in annotations]))
    return _pixels_per_class(annotations, labels)


def _counts_per_class(annotations, labels):
    cpc = {label_name: 0 for label_name in labels.names}
    for annotation in annotations:
        cpc[annotation.label.name] += 1
    return cpc


def _pixels_per_class(annotations, labels):
    ppc = {label_name: 0 for label_name in labels.names}
    for annotation in annotations:
        ppc[annotation.label.name] += int(annotation.area)
    return ppc


def cv2_polygonize(
    mask, dilation_iterations=0, erose_iterations=0, fill_holes=False, values=None
):

    if values is None:
        values = np.unique(mask)

    all_polygons = {}

    for value in values:
        tmp_mask = np.copy(mask)
        tmp_mask[tmp_mask != value] = 0
        tmp_mask[tmp_mask == value] = 1

        if dilation_iterations > 0:
            tmp_mask = binary_dilation(tmp_mask, iterations=dilation_iterations).astype(
                np.uint8
            )

        if fill_holes:
            tmp_mask = binary_fill_holes(tmp_mask).astype(np.uint8)

        if erose_iterations > 0:
            tmp_mask = binary_erosion(tmp_mask, iterations=erose_iterations).astype(
                np.uint8
            )

        tmp_mask = np.pad(
            array=tmp_mask, pad_width=1, mode="constant", constant_values=0
        )

        polygons, _ = cv2.findContours(
            tmp_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE, offset=(-1, -1)
        )

        polygons = [
            np.array(polygon[:, 0, :]) for polygon in polygons if len(polygon) >= 3
        ]
        all_polygons[value] = polygons
    return all_polygons


def plot_annotations(
    annotations: List[Annotation],
    ax=None,
    color_map=None,
    title="",
    use_base_coordinates=False,
    scale=1.0,
):
    ax = ax or plt

    for annotation in annotations:
        color = (
            color_map[annotation.label.name]
            if color_map is not None
            else annotation.label.color
        )

        if use_base_coordinates:
            coordinates = annotation.base_coordinates * scale
        else:
            coordinates = annotation.coordinates * scale

        if isinstance(annotation, Point):
            ax.scatter(*coordinates, color=annotation.label.color)
        elif isinstance(annotation, Polygon):
            ax.plot(*list(zip(*coordinates)), color=color, linewidth=2)
        else:
            raise ValueError(f"invalid annotation {type(annotation)}")

    if ax == plt:
        plt.axis("equal")
        plt.show()
    else:
        ax.axis("equal")
        ax.set_title(title)


def convert_annotations_to_json(annotations: List[Annotation]):
    output = []
    for annotation in annotations:
        output.append(annotation.todict())
    return output


def write_json_annotations(output_path, data, validate=True):
    if validate:
        for d in data:
            jsonschema.validate(d, SCHEMA)

    with open(output_path, "w") as outfile:
        json.dump(data, outfile)
