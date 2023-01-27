from typing import List

from shapely import geometry
from rtree import index

from wholeslidedata.annotation.types import Annotation


def sort_by_area_with_roi(annotations):
    def sort(item):
        if item.label.name in ["roi", "rois", "none"]:
            return 100000 * 100000
        return item.area
    return sorted(annotations, key=lambda item: sort(item), reverse=True)

def sort_by_label_value(annotations):
    return sorted(annotations, key=lambda item: item.label.value)


class AnnotationSelector:
    def __init__(self, annotations: List[Annotation], sorters):
        self._annotations = annotations
        self._sorters = sorters
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

        for sorter in self._sorters:
            annotations = sorter(annotations)
        return annotations
