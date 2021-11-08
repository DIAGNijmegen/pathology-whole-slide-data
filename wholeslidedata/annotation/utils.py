from typing import List

from matplotlib import pyplot as plt
from wholeslidedata.annotation.structures import Annotation, Point, Polygon
from wholeslidedata.labels import Labels
import numpy as np


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
            coordinates = annotation.base_coordinates
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


def shift_coordinates(coordinates, center_x, center_y, width, height, ratio):
    coordinates -= np.array([int(center_x), int(center_y)])
    coordinates /= ratio
    coordinates += np.array([width // 2, height // 2])
    return coordinates