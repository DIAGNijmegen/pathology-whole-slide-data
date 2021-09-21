from typing import List, Optional
import cv2
import numpy as np
from skimage.transform import rescale
from wholeslidedata.annotation.structures import Point, Polygon
from wholeslidedata.annotation.utils import shift_coordinates
from wholeslidedata.image.wholeslideimage import WholeSlideImage
from wholeslidedata.samplers.sampler import Sampler


class PatchLabelSampler(Sampler):
    """[summary]

    Args:
        Sampler ([type]): [description]

    Raises:
        ValueError: [description]

    Returns:
        [type]: [description]
    """

    def sample(
        self,
        wsa,
        point,
        size,
        ratio,
    ):
        """[summary]

        Args:
            wsa ([type]): [description]
            point ([type]): [description]
            size ([type]): [description]
            ratio ([type]): [description]

        Raises:
            ValueError: [description]

        Returns:
            [type]: [description]
        """


@PatchLabelSampler.register(("mask",))
class MaskPatchLabelSampler(PatchLabelSampler):
    def __init__(self, image_backend, ratio):
        self._image_backend = image_backend
        self._ratio = ratio

    # annotation should be coupled to image_annotation. how?
    def sample(
        self,
        wsa,
        point,
        size,
        ratio,
    ):
        x, y = point
        width, height = size
        mask = WholeSlideImage(wsa.path, backend=self._image_backend)
        spacing = mask.spacings[0]

        mask_patch = np.array(
            mask.get_patch(
                int(x // self._ratio),
                int(y // self._ratio),
                int(width // self._ratio),
                int(height // self._ratio),
                spacing=spacing,
                center=True,
                relative=True,
            )
        )[..., 0]

        mask.close()
        mask = None
        del mask

        # upscale
        if self._ratio > 1:
            mask_patch = rescale(
                mask_patch.squeeze().astype("uint8"),
                self._ratio,
                order=0,
                preserve_range=True,
            )

        return mask_patch.astype(np.uint8)


@PatchLabelSampler.register(("segmentation",))
class SegmentationPatchLabelSampler(PatchLabelSampler):
    def __init__(self):
        pass

    # annotation should be coupled to image_annotation. how?
    def sample(
        self,
        wsa,
        point,
        size,
        ratio,
    ):
        center_x, center_y = point
        width, height = size

        # get annotations
        annotations = wsa.select_annotations(
            center_x, center_y, (width * ratio) - 1, (height * ratio) - 1
        )

        # create mask placeholder
        mask = np.zeros((height, width), dtype=np.int32)
        # set labels of all selected annotations
        for annotation in annotations:
            coordinates = annotation.coordinates()
            coordinates = shift_coordinates(
                coordinates, center_x, center_y, width, height, ratio
            )

            if isinstance(annotation, Polygon):
                holemask = np.ones((width, height), dtype=np.int32) * -1
                for hole in annotation.holes():
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


@PatchLabelSampler.register(("classification",))
class ClassificationPatchLabelSampler(PatchLabelSampler):
    def __init__(self):
        pass

    def sample(
        self,
        wsa,
        point,
        size,
        ratio,
    ):
        center_x, center_y = point

        # get annotations
        annotations = wsa.select_annotations(center_x, center_y, 1, 1)

        return np.array([annotations[-1].label.value])


@PatchLabelSampler.register(("detection",))
class DetectionPatchLabelSampler(PatchLabelSampler):

    def __init__(self, max_number_objects: int, detection_labels: List[str], point_box_sizes: Optional[dict] = None):
        self._max_number_objects = max_number_objects
        self._point_box_sizes = point_box_sizes
        self._detection_labels = detection_labels


    def sample(
        self,
        wsa,
        point,
        size,
        ratio,
    ):
        center_x, center_y = point
        width, height = size

        # Get annotations
        annotations = wsa.select_annotations(
            center_x, center_y, (width * ratio) - 1, (height * ratio) - 1
        )

        if len(annotations) > self._max_number_objects:
            raise ValueError(
                f"to many objects in ground truth: {len(annotations)} with possible max number of objects: {self._max_number_objects}"
            )

        objects = np.zeros((self._max_number_objects, 6))
        idx=0
        for annotation in annotations:
            if annotation.label.name not in self._detection_labels:
                continue

            if isinstance(annotation, Point):

                coordinates = shift_coordinates(
                    annotation.coordinates(), center_x, center_y, width, height, ratio
                )

                size = np.array(self._point_box_sizes[annotation.label.name])
          
                objects[idx][0] = max(0, coordinates[0] - (size // 2))
                objects[idx][1] = max(0, coordinates[1] - (size // 2))
                objects[idx][2] = max(0, coordinates[0] + (size // 2))
                objects[idx][3] = max(0, coordinates[1] + (size // 2))

            if isinstance(annotation, Polygon):
                xy1_coordinates = shift_coordinates(
                    np.array(annotation.bounds[:2], dtype='float64'),
                    center_x,
                    center_y,
                    width,
                    height,
                    ratio,
                )

                xy2_coordinates = shift_coordinates(
                    np.array(annotation.bounds[2:], dtype='float64'),
                    center_x,
                    center_y,
                    width,
                    height,
                    ratio,
                )

                objects[idx][:2] = xy1_coordinates
                objects[idx][2:4] = xy2_coordinates

            objects[idx][4] = annotation.label.value
            objects[idx][5] = 1  # confidence
            idx += 1
        return objects
