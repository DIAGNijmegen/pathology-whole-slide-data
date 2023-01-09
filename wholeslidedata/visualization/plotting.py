from typing import List
import matplotlib.patches as pltpatches
import matplotlib.pyplot as plt
from matplotlib import colors

from wholeslidedata.visualization.color import get_color
from wholeslidedata.annotation.types import (
    Annotation,
    PointAnnotation,
    PolygonAnnotation,
)

import numpy as np

def plot_annotations(
    annotations: List[Annotation],
    ax=None,
    color_map=None,
    title="",
    use_base_coordinates=False,
    scale=1.0,
):
    ax = ax or plt

    if use_base_coordinates:
        min_x = min(annotation.bounds[0] for annotation in annotations)
        min_y = min(annotation.bounds[1] for annotation in annotations)
        annotations = [annotation.translate((min_x, min_y)) for annotation in annotations]

    for annotation in annotations:
        color = get_color(annotation, color_map)
        coordinates = np.array(annotation.coordinates) * scale

        if isinstance(annotation, PointAnnotation):
            ax.scatter(*coordinates, color=color)
        elif isinstance(annotation, PolygonAnnotation):
            ax.plot(*list(zip(*coordinates)), color=color, linewidth=2)
        else:
            raise ValueError(f"invalid annotation {type(annotation)}")

    if ax == plt:
        plt.axis("equal")
        plt.gca().invert_yaxis()
        plt.show()
    else:
        ax.axis("equal")
        ax.invert_yaxis()
        ax.set_title(title)


"""Plotting"""


def plot_batch(x_batch, y_batch, alpha=0.4, size=(20, 5)):
    fig, axes = plt.subplots(1, len(x_batch), figsize=size)
    for batch_index in range(len(x_batch)):
        axes[batch_index].imshow(x_batch[batch_index])
        plot_mask(y_batch[batch_index], axes=axes[batch_index], alpha=alpha)
    plt.tight_layout()
    plt.show()


def plot_batch_overlay(x_batch, y_batch, output_shape=None):
    for batch_index in range(len(x_batch)):
        fig, axes = plt.subplots(1, 1, figsize=(10, 10))
        plot_patch(x_batch[batch_index], axes=axes)
        plot_mask(y_batch[batch_index], axes=axes, output_shape=output_shape)
        plt.show()


def plot_batch_detection(x_batch, y_batch, output_shape=None, color_map=plt.cm.Paired):
    """
    Plot batch function for ground truth labels provided by DetectionLabelSampler class.
    """
    fig, axes = plt.subplots(1, x_batch.shape[0], figsize=(20, 5))
    for batch_index in range(len(x_batch)):
        plot_patch(x_batch[batch_index], axes=axes[batch_index])
        plot_boxes(
            y_batch[batch_index],
            axes=axes[batch_index],
            output_shape=output_shape,
            color_map=color_map,
            max_width=x_batch[batch_index].shape[1],
            max_height=x_batch[batch_index].shape[0],
        )
    plt.show()


def plot_boxes(
    boxes, max_width, max_height, axes=None, output_shape=None, color_map=plt.cm.prism
):
    if axes is None:
        _, ax = plt.subplots(1, 1)
    else:
        ax = axes

    for box in boxes:
        x1, y1, x2, y2, label_value, confidence = box
        color = color_map(int(label_value))

        if (x1, y1, x2, y2) != (0, 0, 0, 0):
            rect = pltpatches.Rectangle(
                (x1, y1),
                min(max_width, max(0, x2 - x1)),
                min(max_height, max(0, y2 - y1)),
                linewidth=2,
                edgecolor="red",
                facecolor="none",
            )
            ax.add_patch(rect)

    if axes is None:
        plt.show()


def plot_patch(patch, axes=None, title="my_patch", output_size=None, alpha=1.0):
    if axes is None:
        _, ax = plt.subplots(1, 1)
    else:
        ax = axes

    ax.imshow(patch, alpha=alpha)
    if axes is None:
        plt.show()


def plot_mask(
    mask,
    color_values=[
        "white",
        "red",
        "blue",
        "green",
        "orange",
        "brown",
        "yellow",
        "purple",
        "pink",
        "grey",
    ],
    axes=None,
    title="",
    alpha=1.0,
):

    cmap = colors.ListedColormap(color_values)
    bounds = list(range(len(color_values) + 1))
    norm = colors.BoundaryNorm(bounds, cmap.N, clip=True)

    if axes is None:
        _, ax = plt.subplots(1, 1)
    else:
        ax = axes

    ax.imshow(mask, cmap=cmap, norm=norm, interpolation="nearest", alpha=alpha)
    ax.set_title(title)

    if axes is None:
        plt.show()


def plot_one_hot_batch(x_batch, y_batch, label_map):
    for batch_index in range(2):
        fig, axes = plt.subplots(
            1, y_batch[batch_index].shape[-1] + 1, figsize=(20, 60)
        )
        axes[0].imshow(x_batch[batch_index])
        for one_hot_index in range(y_batch[batch_index].shape[-1]):
            axes[one_hot_index + 1].imshow(y_batch[batch_index][:, :, one_hot_index])
            axes[one_hot_index + 1].set_title(
                list(
                    map(
                        lambda label: label_map[label],
                        np.unique(y_batch[batch_index][:, :, one_hot_index])
                        * (one_hot_index + 1),
                    )
                )
            )
        plt.show()

