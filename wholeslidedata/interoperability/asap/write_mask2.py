from pathlib import Path
from typing import List

import cv2
import numpy as np
from shapely import geometry
from shapely.strtree import STRtree
from wholeslidedata.annotation.structures import Annotation, Point, Polygon
from wholeslidedata.image.wholeslideimage import WholeSlideImage
from wholeslidedata.accessories.asap.imagewriter import WholeSlideMaskWriter
from wholeslidedata.samplers.utils import shift_coordinates


def select_annotations(
    stree: STRtree, center_x: int, center_y: int, width: int, height: int
):
    box = geometry.box(
        center_x - width // 2,
        center_y - height // 2,
        center_x + width // 2,
        center_y + height // 2,
    )
    annotations = stree.query(box)

    return sorted(annotations, key=lambda item: item.area, reverse=True)


def get_mask(stree, point, size, ratio):

    center_x, center_y = point.x, point.y
    width, height = size

    # get annotations
    annotations = select_annotations(
        stree, center_x, center_y, (width * ratio) - 1, (height * ratio) - 1
    )

    # create mask placeholder
    mask = np.zeros((height, width), dtype=np.int32)
    # set labels of all selected annotations
    for annotation in annotations:
        coordinates = np.copy(annotation.coordinates)
        coordinates = shift_coordinates(
             coordinates, center_x, center_y, width, height, ratio
        )

        if isinstance(annotation, Polygon):
            holemask = np.ones((height, width), dtype=np.int32) * -1
            for hole in annotation.holes:
                hcoordinates = shift_coordinates(
                    hole, center_x, center_y, width, height, ratio
                )
                cv2.fillPoly(holemask, np.array([hcoordinates], dtype=np.int32), 1)
                holemask[holemask != -1] = mask[holemask != -1]
            cv2.fillPoly(
                mask,
                np.array([coordinates], dtype=np.int32),
                annotation.label.value,
            )
            mask[holemask != -1] = holemask[holemask != -1]

        elif isinstance(annotation, Point):
            mask[int(coordinates[1]), int(coordinates[0])] = annotation.label.value

    return mask.astype(np.uint8)


def convert_annotations_to_mask(
    wsi: WholeSlideImage,
    annotations: List[Annotation],
    spacing: float,
    mask_output_path: Path,
    tile_size: int = 1024,
):
    stree = STRtree(annotations)
    ratio = wsi.get_downsampling_from_spacing(spacing)
    shape = wsi.shapes[wsi.get_level_from_spacing(spacing)]
    ratio = wsi.get_downsampling_from_spacing(spacing)
    write_spacing = wsi.get_real_spacing(spacing)

    wsm_writer = WholeSlideMaskWriter()
    wsm_writer.write(
        path=mask_output_path,
        spacing=write_spacing,
        dimensions=(shape[0], shape[1]),
        tile_shape=(tile_size, tile_size),
    )

    for y_pos in range(0, shape[1], tile_size):
        for x_pos in range(0, shape[0], tile_size):
            mask = get_mask(
                stree,
                geometry.Point(
                    (x_pos + tile_size // 2) * ratio,
                    (y_pos + tile_size // 2) * ratio,
                ),
                (tile_size, tile_size),
                ratio,
            )
            if np.any(mask):
                wsm_writer.write_tile(tile=mask, coordinates=(int(x_pos), int(y_pos)))

    print("closing...")
    wsm_writer.save()
    print("done")
