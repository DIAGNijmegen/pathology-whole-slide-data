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

        return (annotations[-1].label.value, )


@PatchLabelSampler.register(("detection",))
class DetectionPatchLabelSampler(PatchLabelSampler):
    def __init__(self):
        super().__init__()

    def sample(
        self,
        wsa,
        point,
        size,
        ratio,
        label_name_to_bounding_box_map=None,
    ):

        center_x, center_y = point
        width, height = size

        # Get annotations
        annotations = wsa.select_annotations(
            center_x, center_y, (width * ratio) - 1, (height * ratio) - 1
        )

        # Return object tuple of label, center coordinates, width/height
        # for all points in region
        objects = []
        for annotation in annotations:
            label = annotation.label.value
            name = annotation.label.name

            # If Point, create fixed width/height
            if isinstance(annotation, Point):
                center_x_anno, center_y_anno = annotation.coordinates()
                if label_name_to_bounding_box_map is not None:
                    width_anno, height_anno = label_name_to_bounding_box_map[name]
                elif hasattr(annotation.label, "boundingbox"):
                    width_anno, height_anno = annotation.label.boundingbox
                else:
                    raise ValueError(
                        "No label to bounding box map or bounding box attribute in annotation"
                    )

            # If Polygon, use bounds
            if isinstance(annotation, Polygon):
                center_x_anno, center_y_anno = annotation.center
                width_anno, height_anno = annotation.size

            objects.append(
                (label, center_x_anno, center_y_anno, width_anno, height_anno)
            )
        return objects
