from typing import List

from matplotlib import pyplot as plt
from wholeslidedata.annotation.structures import Annotation, Point, Polygon
from wholeslidedata.labels import Labels
import numpy as np


class Within(object):
    def __init__(self, o):
        self.o = o

    def __lt__(self, other):
        return self.o.buffer(0).within(other.o.buffer(0))


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


def plot_annotations(annotations: List[Annotation], ax=None, title="", use_base_coordinates=False):
    ax = ax or plt

    for annotation in annotations:
        if use_base_coordinates:
            coordinates = annotation.base_coordinates
        else:
            coordinates = annotation.coordinates()

        if isinstance(annotation, Point):
            ax.scatter(*coordinates, color=annotation.label.color)
        elif isinstance(annotation, Polygon):
            ax.plot(*list(zip(*coordinates)), color=annotation.label.color, linewidth=4)
        else:
            raise ValueError(f"invalid annotation {type(annotation)}")

    if ax == plt:
        plt.gca().invert_yaxis()
        plt.axis("equal")
        plt.show()
    else:
        ax.axis("equal")
        ax.invert_yaxis()
        ax.set_title(title)


def shift_coordinates(coordinates, center_x, center_y, width, height, ratio):
    coordinates -= np.array([center_x, center_y])
    coordinates /= ratio
    coordinates += np.array([width // 2, height // 2])
    return coordinates