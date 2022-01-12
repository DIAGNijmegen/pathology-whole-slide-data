import time
from xml.dom import minidom
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Comment, Element, ElementTree, SubElement, tostring

import matplotlib.pyplot as plt
import matplotlib.patches as pltpatches
import numpy as np
from matplotlib import colors


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if "log_time" in kw:
            name = kw.get("log_name", method.__name__.upper())
            kw["log_time"][name] = int((te - ts) * 1000)
        else:
            print("%r  %2.2f ms" % (method.__name__, (te - ts) * 1000))
        return result

    return timed


def block_shaped(arr, nrows, ncols):
    if len(arr.shape) == 3:
        height, _, channels = arr.shape
        return (
            arr.reshape(height // nrows, nrows, -1, ncols, channels)
            .swapaxes(1, 2)
            .reshape(-1, nrows, ncols, channels)
        )
    elif len(arr.shape) == 2:
        height, _ = arr.shape
        return (
            arr.reshape(height // nrows, nrows, -1, ncols)
            .swapaxes(1, 2)
            .reshape(-1, nrows, ncols)
        )


def unblockshaped(arr, h, w):
    _, nrows, ncols, channels = arr.shape
    return (
        arr.reshape(h // nrows, -1, nrows, ncols, channels)
        .swapaxes(1, 2)
        .reshape(h, w, channels)
    )


def one_hot_encoding(mask, label_map, ignore_zero=True):
    """Encodes mask into one hot encoding."""
    ncols = max(label_map.values()) + 1
    out = np.zeros((mask.size, ncols), dtype=np.uint8)
    out[np.arange(mask.size), mask.ravel()] = 1
    out.shape = mask.shape + (ncols,)
    if 0 in label_map.values() and not ignore_zero:
        return out
    return out[..., 1:]


def one_hot_decoding(mask, base=-1):
    """decode one hot encoding"""
    xs, ys, lbl = np.where(mask)
    new_mask = np.zeros((mask.shape[0], mask.shape[1]))
    new_mask[xs, ys] = lbl.astype(int) + 1
    return new_mask + base

def clean_weights(masks):
    return np.clip(np.sum(masks, axis=-1), 0, 1)


def shift_coordinates(coordinates, center_x, center_y, width, height, ratio):
    coordinates = np.array(coordinates, dtype='float')
    coordinates -= np.array([center_x, center_y], dtype='float')
    coordinates /= ratio
    coordinates += np.array([width // 2, height // 2])
    return coordinates


def normalize(input_):
    _type = type(input_)
    if _type == np.ndarray:
        return input_ / 255.0
    return _type(np.array(input_) / 255.0)


def fit_data(data, output_shape):

    if (data.shape[0] == output_shape[0]) and (data.shape[1] == output_shape[1]):
        return data

    cropx = (data.shape[0] - output_shape[0]) // 2
    cropy = (data.shape[1] - output_shape[1]) // 2

    if len(data.shape) == 2:
        return data[cropx:-cropx, cropy:-cropy]
    if len(data.shape) == 3:
        return data[cropx:-cropx, cropy:-cropy, :]
    if len(data.shape) == 4:
        cropx = (data.shape[1] - output_shape[0]) // 2
        cropy = (data.shape[2] - output_shape[1]) // 2
        return data[:, cropx:-cropx, cropy:-cropy, :]
    if len(data.shape) == 5:
        cropx = (data.shape[2] - output_shape[0]) // 2
        cropy = (data.shape[3] - output_shape[1]) // 2
        return data[:, :, cropx:-cropx, cropy:-cropy, :]


def resolve_detection_batch(y_batch):
    return y_batch[~np.all(y_batch == 0, axis=-1)]


def resolve_classification_batch(y_batch):
    return np.squeeze(y_batch)


"""Plotting"""


def plot_batch(x_batch, y_batch, output_shape=None, axes=None):
    if axes is not None and len(axes) != len(x_batch) * 2:
        raise ValueError(
            f"axes dims {len(axes)}  do not correspond to samples {len(x_batch)} in batch"
        )

    for batch_index in range(len(x_batch)):
        if axes is None:
            fig, axes = plt.subplots(1, 2, figsize=(10, 10))
        plot_patch(x_batch[batch_index], axes=axes[0])
        # plot_mask(y_batch[batch_index], axes=axes[1], output_shape=output_shape)
        if axes is None:
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

    for batch_index in range(len(x_batch)):
        fig, axes = plt.subplots(1, 1, figsize=(10, 10))
        plot_patch(x_batch[batch_index], axes=axes)
        plot_boxes(
            y_batch[batch_index],
            axes=axes,
            output_shape=output_shape,
            color_map=color_map,
        )
        plt.show()


def plot_boxes(boxes, axes=None, output_shape=None, color_map=plt.cm.prism):
    if axes is None:
        _, ax = plt.subplots(1, 1)
    else:
        ax = axes

    for box in boxes:
        x1, y1, x2, y2, label_value, confidence = box
        color = color_map(int(label_value))
        rect = pltpatches.Rectangle(
            (x1, y1), x2 - x1, y2 - y1, linewidth=2, edgecolor=color, facecolor="none"
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
    color_values=["white", "red", "blue", "green", "orange", 'brown', 'yellow', 'purple', 'pink', 'grey'],
    axes=None,
    title="",
    output_shape=None,
    alpha=1.0,
):

    if output_shape:
        mask = fit_data(mask, output_shape)

    cmap = colors.ListedColormap(color_values)
    bounds=list(range(len(color_values)))
    norm = colors.BoundaryNorm(bounds, cmap.N, clip=True)

    if axes is None:
        _, ax = plt.subplots(1, 1)
    else:
        ax = axes

    ax.imshow(mask, cmap=cmap, norm=norm, interpolation='nearest', alpha=alpha)
    ax.set_title(title)

    if axes is None:
        plt.show()

def get_one_hot_label_name(label_map):
    def get_label(label):
        return label_map[label]

    return get_label


def plot_on_hot_batch(x_batch, y_batch, label_map):
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
                        get_one_hot_label_name(label_map),
                        np.unique(y_batch[batch_index][:, :, one_hot_index])
                        * (one_hot_index + 1),
                    )
                )
            )
        plt.show()


def plot_annotations(annotations, axes=None):
    for annotation in annotations:
        if axes == None:
            if annotation.type == "Point":
                plt.scatter(*annotation.coordinates)
            else:
                plt.plot(*list(zip(*annotation.coordinates)))
            plt.gca().invert_yax.datais()
            plt.axis("equal")
            plt.show()
        else:
            if annotation.type == "Point":
                axes.scatter(*annotation.coordinates)
            else:
                axes.plot(*list(zip(*annotation.coordinates)))


def convert_image_annotation_to_xml(image_annotation, out_path, label_map, color_map):
    def write_text(path, text):
        with open(str(path), "w") as the_file:
            the_file.write(text)

    def prettify(elem):
        """Return a pretty-printed XML string for the Element."""
        rough_string = ET.tostring(elem, "utf-8")
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    top = Element("ASAP_Annotations")
    groups = SubElement(top, "AnnotationGroups")
    for lab in label_map:
        groupel = SubElement(
            groups,
            "Group",
            attrib=dict(Name=lab, PartOfGroup="None", Color=color_map[lab]),
        )

    annosel = SubElement(top, "Annotations")
    for i, p in enumerate(image_annotation.annotations):

        annoel = SubElement(
            annosel,
            "Annotation",
            attrib=dict(
                Name=f"Annotation {i}",
                Type="Polygon",
                PartOfGroup=p.label_name,
                Color=color_map[p.label_name],
            ),
        )
        coordsel = SubElement(annoel, "Coordinates")
        coords = p._coordinates
        for i_, coord in enumerate(coords):
            coordel = SubElement(
                coordsel,
                "Coordinate",
                attrib=dict(Order=str(i_), X=str(coord[0]), Y=str(coord[1])),
            )
    # print(prettify(top))
    xml_string = prettify(top)
    write_text(out_path, xml_string)
    # ElementTree(top).write(out_path)
    print("%s saved" % out_path)
