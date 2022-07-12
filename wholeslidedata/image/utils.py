import cv2

from bisect import bisect_left
import numpy as np

from wholeslidedata.annotation.structures import Annotation
from wholeslidedata.samplers.utils import shift_coordinates

def take_closest_level(spacings, spacing):
    pos = bisect_left(spacings, spacing)
    if pos == 0:
        return pos
    if pos == len(spacings):
        return pos - 1
    if spacings[pos] - spacing < spacing - spacings[pos - 1]:
        return pos
    return pos - 1


def create_thumbnail(wsi, output_folder, spacing=8.0):
    slide = wsi.get_slide(spacing)
    output_path = output_folder / (wsi.path.stem + ".png")
    cv2.imwrite(str(output_path), slide)


def mask_patch_with_annotation(patch: np.ndarray, annotation: Annotation, size: tuple, scaling: float, ):
    ratio = 1/scaling
    height= int(size[1]//ratio)
    width = int(size[0]//ratio)
    mask = np.zeros((height, width), dtype=np.int32)
    coordinates = np.copy(annotation.coordinates)
    coordinates = shift_coordinates(
        coordinates, *annotation.center, width, height, ratio
    )
    cv2.fillPoly(
            mask,
            np.array([coordinates], dtype=np.int32),
            annotation.label.value,
        )
    patch[mask == 0] = 0
    return patch