import cv2
import numpy as np
from scipy.ndimage.morphology import binary_dilation, binary_erosion, binary_fill_holes


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



