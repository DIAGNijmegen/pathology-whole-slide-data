from pathlib import Path
from typing import Dict, List, Optional, Union

from rtree import index

from wholeslidedata.annotation import utils as annotation_utils
from wholeslidedata.annotation.labels import Labels
from wholeslidedata.annotation.parser import AnnotationParser
from wholeslidedata.annotation.types import Annotation, PolygonAnnotation
from wholeslidedata.annotation.parsers import PARSERS, DEFAULT_PARSERS
from wholeslidedata.annotation.selector import AnnotationSelector


class WholeSlideAnnotation:
    def __init__(
        self,
        annotation_path: Union[Path, str],
        labels: Optional[Union[Labels, list, tuple, dict]] = None,
        parser: AnnotationParser = None,
        ignore_overlap: bool = True,
        **kwargs
    ):
        """WholeSlideAnnotation contains all annotions of an whole slide image

        Args:
            annotation_path (Union[Path, str]): path to annotation file
            labels (Optional[Union[Labels, list, tuple, dict]], optional): labels to be used from annotation file. Defaults to None.
            renamed_labels (Optional[Union[Labels, list, tuple, dict]], optional): rename labels. Defaults to None.
            parser (AnnotationParser, optional): annotation parser. Defaults to "asap".
            sort_by_overlay_index (bool, optional): if true, selecting annotions will be sorted by overlay index when . Defaults to False.
            ignore_overlap (bool, optional): if true overlapping annotations will be not set. Defaults to True.
            kwargs is reserved for the initialization of the parser

        """
        self._annotation_path = Path(annotation_path)
        self._spacing  = kwargs.pop('spacing', None)
        self._parser = self._init_parser(
            parser, self._annotation_path, labels, **kwargs
        )
        self._annotations = self._parser.parse(self._annotation_path, self._spacing)
        self._labels = annotation_utils.get_labels_in_annotations(self.annotations)
        self._sample_labels = self._parser.sample_label_names
        self._sample_types = self._parser.sample_annotation_types

        self._sampling_annotations = []
        for annotation in self._annotations:
            if not self._sample_labels or annotation.label.name in self._sample_labels:
                if not self._sample_types or annotation.type in self._sample_types:
                    self._sampling_annotations.append(annotation)

        if not ignore_overlap:
            self._set_overlapping_annotations()

        self._annotation_selector = AnnotationSelector(self._annotations, sorters=self._parser.sorters)

    def _init_parser(self, parser, annotation_path, labels, **kwargs):
        if isinstance(parser, AnnotationParser):
            return parser
        if isinstance(parser, str):
            return PARSERS[parser](labels=labels, **kwargs)
        if parser is None:
            return DEFAULT_PARSERS[Path(annotation_path).suffix](
                labels=labels, **kwargs
            )
        return parser(labels=labels, **kwargs)

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
        return self._sampling_annotations

    @property
    def annotations_per_label(self) -> Dict[str, List[Annotation]]:
        return self._get_annotations_per_label(self.annotations)

    @property
    def sampling_annotations_per_label(self) -> Dict[str, List[Annotation]]:
        return self._get_annotations_per_label(self.sampling_annotations)

    def _get_annotations_per_label(
        self, annotations: List[Annotation]
    ) -> Dict[str, List[Annotation]]:
        annos_per_label = dict()
        for annotation in annotations:
            annos_per_label.setdefault(annotation.label.name, []).append(annotation)
        return annos_per_label

    def _set_overlapping_annotations(self):
        for annotation_index, annotation in enumerate(self._annotations[:-1]):
            if isinstance(annotation, PolygonAnnotation):
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

        return self._annotation_selector.select_annotations(
            center_x, center_y, width, height
        )

    def __repr__(self):
        return str(self.path)