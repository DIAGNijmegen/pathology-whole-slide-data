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
import cv2

MASK_COLOR_VALUES = [
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
    ]

def plot_coordinates(image, coordinates, border_rgb, thickness=1, fill_rgb=None, alpha=1):
    overlay = image.copy()
    overlay = cv2.polylines(overlay, [np.int32(coordinates)], True, color=border_rgb, thickness=thickness)
    if fill_rgb is not None:
        overlay = cv2.fillPoly(overlay,  [np.int32(coordinates)], color=fill_rgb)
    return cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)
    

# do offset and ratio outside this function
def annotations_to_mask(image, annotations, offset, color_map, ratio, fill=False):
    for annotation in annotations:
        rgb_color = color_map[annotation.label.name]
        coordinates = (annotation.coordinates -np.array(offset)) /ratio
        if fill:
            image = plot_coordinates(image, coordinates, border_rgb=rgb_color, fill_rgb=rgb_color)
        else:
            image = plot_coordinates(image, coordinates, border_rgb=rgb_color)
    return image


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
        holes = [np.array(hole) * scale for hole in annotation.holes]

        if isinstance(annotation, PointAnnotation):
            ax.scatter(*coordinates, color=color)
        elif isinstance(annotation, PolygonAnnotation):
            ax.plot(*list(zip(*coordinates)), color=color, linewidth=2)
        else:
            raise ValueError(f"invalid annotation {type(annotation)}")

        for hole in holes:
            ax.plot(*list(zip(*hole)), color=color, linewidth=2)

    if ax == plt:
        plt.axis("equal")
        plt.gca().invert_yaxis()
        plt.show()
    else:
        ax.axis("equal")
        ax.set_title(title)


"""Plotting"""


def plot_batch(x_batch, y_batch, alpha=0.4, size=(20, 5), color_values=None):
    fig, axes = plt.subplots(1, len(x_batch), figsize=size)
    for batch_index in range(len(x_batch)):
        axes[batch_index].imshow(x_batch[batch_index])
        plot_mask(y_batch[batch_index], axes=axes[batch_index], alpha=alpha, color_values=color_values)
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


def plot_patch(patch, ax=None, alpha=1.0):
    if ax is None:
        _, ax = plt.subplots(1, 1)
    else:
        ax = ax

    ax.imshow(patch, alpha=alpha)

    if ax is None:
        plt.show()


def plot_mask(
    mask,
    color_values=None,
    axes=None,
    title="",
    alpha=1.0,
):
    
    if color_values is None:
        color_values = MASK_COLOR_VALUES
    
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


def plot_one_hot_batch(x_batch, y_batch, color_map, label_value_map):
    for batch_index in range(x_batch.shape[0]):
        fig, axes = plt.subplots(
            1, y_batch[batch_index].shape[-1] + 1, figsize=(20, 60)
        )
        axes[0].imshow(x_batch[batch_index])
        for one_hot_index in range(y_batch[batch_index].shape[-1]):
            
            mask = y_batch[batch_index][:, :, one_hot_index]
            # create another mask to place color in white regions
            im = np.zeros((mask.shape)+(3,), np.uint8)
            im[mask == 1] = color_map[one_hot_index]
            
            axes[one_hot_index + 1].imshow(im)
            axes[one_hot_index + 1].set_title(label_value_map[one_hot_index].name)
        plt.show()

