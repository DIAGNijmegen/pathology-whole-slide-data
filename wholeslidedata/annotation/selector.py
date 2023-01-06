
from typing import List

from shapely import geometry
from rtree import index

from wholeslidedata.annotation.types import Annotation


def area_sort_with_roi(item):
    if item.label.name in ["roi", "rois", "none"]:
        return 100000 * 100000
    return item.area


class AnnotationSelector:
    def __init__(self, annotations: List[Annotation]):
        self._annotations = annotations
        self._tree = index.Index()
        for pos, annotation in enumerate(annotations):
            self._tree.insert(pos, annotation.bounds)

    def select_annotations(
        self, center_x: int, center_y: int, width: int, height: int
    ) -> List[Annotation]:
        """Selects annotations within specific region and sorts accordingly

        Args:
            center_x (int): x center of region
            center_y (int): y center of region
            width (int): width of region
            height (int): height of region

        Returns:
            List[Annotation]: all annotations that overlap with specified region
        """

        box = geometry.box(
            center_x - width // 2,
            center_y - height // 2,
            center_x + width // 2,
            center_y + height // 2,
        )

        annotations = [
            self._annotations[pos] for pos in self._tree.intersection(box.bounds)
        ]

        # TODO add custom sort function, e.g., overlay index

        # sort by label value
        sorted_annotations = sorted(annotations, key=lambda item: item.label.value)

        # sort by area, (roi,rois,none lowest)
        sorted_annotations = sorted(
            sorted_annotations, key=lambda item: area_sort_with_roi(item), reverse=True
        )
        return sorted_annotations