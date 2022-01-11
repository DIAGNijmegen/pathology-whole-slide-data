from pathlib import Path
from typing import List, Optional, Union

from shapely import geometry
from shapely.strtree import STRtree
from wholeslidedata.annotation.structures import Annotation, Polygon
from wholeslidedata.annotation.parsers import AnnotationParser
from wholeslidedata.annotation import utils as annotation_utils
from wholeslidedata.labels import Labels


def area_sort_with_roi(item):
    if item.label.name == "roi" or item.label.name == "rois":
        return 100000 * 100000
    return item.area


class WholeSlideAnnotation:
    # fix for strtree segmentation fault bug
    STREE = {}

    def __init__(
        self,
        annotation_path: Union[Path, str],
        labels: Optional[Union[Labels, list, tuple, dict]] = None,
        renamed_labels: Optional[Union[Labels, list, tuple, dict]] = None,
        parser: AnnotationParser = "asap",
        sort_by_overlay_index: bool = False,
        ignore_overlap: bool = True,
    ):
        """WholeSlideAnnotation contains all annotions of an whole slide image

        Args:
            annotation_path (Union[Path, str]): path to annotation file
            labels (Optional[Union[Labels, list, tuple, dict]], optional): labels to be used from annotation file. Defaults to None.
            renamed_labels (Optional[Union[Labels, list, tuple, dict]], optional): rename labels. Defaults to None.
            parser (AnnotationParser, optional): annotation parser. Defaults to "asap".
            sort_by_overlay_index (bool, optional): if true, selecting annotions will be sorted by overlay index when . Defaults to False.
            ignore_overlap (bool, optional): if true overlapping annotations will be not set. Defaults to True.

        Raises:
            FileNotFoundError: if annotation file is not found
        """

        self._annotation_path = Path(annotation_path)

        if not self._annotation_path.exists():
            raise FileNotFoundError(self._annotation_path)

        self._annotation_parser = AnnotationParser.create(parser)
        self._annotations = self._annotation_parser.parse(
            annotation_path, labels, renamed_labels
        )

        self._sort_by_overlay_index = sort_by_overlay_index
        self._labels = annotation_utils.get_labels_in_annotations(self.annotations)
        sample_labels = self._annotation_parser.sample_label_names

        self._sampling_annotations = [
            annotation
            for annotation_type in self._annotation_parser.sample_annotation_types
            for annotation in self._annotations
            if isinstance(annotation, annotation_type)
            and (not sample_labels or annotation.label.name in sample_labels)
        ]

        if not ignore_overlap:
            self._set_overlapping_annotations()

        WholeSlideAnnotation.STREE[self] = STRtree(self._annotations)

    @property
    def path(self):
        return self._annotation_path

    @property
    def annotations(self):
        return self._annotations

    @property
    def labels(self):
        return self._labels

    @property
    def sampling_annotations(self) -> List[Annotation]:
        """Annotations that will be used for sampling

        Returns:
            List[Annotation]: list of annotations 
        """
        return self._sampling_annotations

    def _set_overlapping_annotations(self):
        for annotation_index, annotation in enumerate(self._annotations[:-1]):
            if isinstance(annotation, Polygon):
                overlap_tree = STRtree(
                    annotation
                    for annotation in self._annotations[annotation_index + 1 :]
                )

                annotation.add_overlapping_annotations(overlap_tree.query(annotation))

    def select_annotations(self, center_x: int, center_y: int, width: int, height: int) -> List[Annotation]:
        """ Selects annotations within specific region and sorts accordingly 

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
        annotations = WholeSlideAnnotation.STREE[self].query(box)
        if self._sort_by_overlay_index:
            return sorted(
                annotations,
                key=lambda item: self.labels.get_label_by_name(
                    item.label.name
                ).overlay_index,
            )
        sorted_annotations = sorted(
            annotations,
            key=lambda item: self.labels.get_label_by_name(item.label.name).value,
        )
        sorted_annotations = sorted(
            sorted_annotations, key=lambda item: area_sort_with_roi(item), reverse=True
        )
        return sorted_annotations
