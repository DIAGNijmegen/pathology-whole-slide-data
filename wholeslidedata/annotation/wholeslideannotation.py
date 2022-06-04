from pathlib import Path
from typing import Dict, List, Optional, Union
from shapely import geometry
from wholeslidedata.annotation import utils as annotation_utils
from wholeslidedata.annotation.parser import AnnotationParser
from wholeslidedata.annotation.structures import Annotation, Polygon
from wholeslidedata.extensions import (
    ExtensibleMarkupLanguage,
    JavaScriptObjectNotation,
    TaggedImageFileExtension,
    WholeSlideAnnotationExtension,
)
from wholeslidedata.labels import Labels
from rtree import index


def area_sort_with_roi(item):
    if item.label.name in ["roi", "rois", "none"]:
        return 100000 * 100000
    return item.area


DEFAULT_PARSERS = {
    JavaScriptObjectNotation: "wsa",
    ExtensibleMarkupLanguage: "asap",
    TaggedImageFileExtension: "mask",
}


class WholeSlideAnnotation:
    def __init__(
        self,
        annotation_path: Union[Path, str],
        labels: Optional[Union[Labels, list, tuple, dict]] = None,
        parser: AnnotationParser = None,
        sort_by_overlay_index: bool = False,
        ignore_overlap: bool = True
    ):
        """WholeSlideAnnotation contains all annotions of an whole slide image

        Args:
            annotation_path (Union[Path, str]): path to annotation file
            labels (Optional[Union[Labels, list, tuple, dict]], optional): labels to be used from annotation file. Defaults to None.
            renamed_labels (Optional[Union[Labels, list, tuple, dict]], optional): rename labels. Defaults to None.
            parser (AnnotationParser, optional): annotation parser. Defaults to "asap".
            sort_by_overlay_index (bool, optional): if true, selecting annotions will be sorted by overlay index when . Defaults to False.
            ignore_overlap (bool, optional): if true overlapping annotations will be not set. Defaults to True.

        """
        self._annotation_path = annotation_path   
    
        if parser is None:
            parser = DEFAULT_PARSERS[
                WholeSlideAnnotationExtension.get_registrant(
                    Path(self._annotation_path).suffix
                )
            ]

        self._annotation_parser: AnnotationParser = AnnotationParser.create(
            parser, labels=labels
        )
        self._annotations = self._annotation_parser.parse(self._annotation_path)

        self._sort_by_overlay_index = sort_by_overlay_index
        self._labels = annotation_utils.get_labels_in_annotations(self.annotations)
        self._sample_labels = self._annotation_parser.sample_label_names
        self._sample_types = self._annotation_parser.sample_annotation_types

        self._sampling_annotations = []
        for annotation in self._annotations:
            if not self._sample_labels or annotation.label.name in self._sample_labels:
                if not self._sample_types or type(annotation) in self._sample_types:
                    self._sampling_annotations.append(annotation)

        if not ignore_overlap:
            self._set_overlapping_annotations()

        self._tree = index.Index()
        for pos, annotation in enumerate(self._annotations):
            self._tree.insert(pos, annotation.bounds)

    @property
    def path(self):
        return self._annotation_path

    @property
    def labels(self):
        return self._labels

    @property
    def annotations(self):
        return self._annotations

    @property
    def sampling_annotations(self) -> List[Annotation]:
        """Annotations that will be used for sampling

        Returns:
            List[Annotation]: list of annotations
        """
        return self._sampling_annotations

    @property
    def annotations_per_label(self) -> Dict[str, List[Annotation]]:
        return self._get_annotations_per_label(self.annotations)

    @property
    def sampling_annotations_per_label(self) -> Dict[str, List[Annotation]]:
        return self._get_annotations_per_label(self.sampling_annotations)

    def _get_annotations_per_label(self, annotations: List[Annotation]) -> Dict[str, List[Annotation]]:
        annos_per_label = dict()
        for annotation in annotations:
            annos_per_label.setdefault(annotation.label.name, []).append(annotation)
        return annos_per_label

    def _set_overlapping_annotations(self):
        for annotation_index, annotation in enumerate(self._annotations[:-1]):
            if isinstance(annotation, Polygon):
                tree = index.Index()
                annotation_view = self._annotations[annotation_index + 1 :]
                for pos, annotation in enumerate(annotation_view):
                    tree.insert(pos, annotation.bounds)
           
                for pos in tree.intersection(annotation.bounds):
                    annotation.add_overlapping_annotations(annotation_view[pos])

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
