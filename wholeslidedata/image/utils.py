import cv2
import numpy as np

from wholeslidedata.annotation.types import Annotation
from wholeslidedata.samplers.utils import shift_coordinates


def create_thumbnail(wsi, output_folder, spacing=8.0):
    slide = wsi.get_slide(spacing)
    output_path = output_folder / (wsi.path.stem + ".png")
    cv2.imwrite(str(output_path), slide)


def mask_patch_with_annotation(
    patch: np.ndarray, annotation: Annotation, scaling: float, offset=None,
):
    masked_patch = np.copy(patch)
    if offset is None:
        coordinates = np.array(annotation.base_coordinates) * scaling
    else:
        coordinates = (np.array(annotation.coordinates) - np.array([offset[0], offset[1]])) * scaling

    mask = np.zeros((masked_patch.shape[:2]), dtype=np.int32)
    cv2.fillPoly(mask, np.array([coordinates], dtype=np.int32), 1)
    masked_patch[mask == 0] = 0
    return masked_patch