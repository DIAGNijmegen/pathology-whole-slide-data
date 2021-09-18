from pathlib import Path

from shapely import geometry
from shapely.strtree import STRtree
from wholeslidedata.labels import Labels
from wholeslidedata.annotation.structures import Polygon
from wholeslidedata.annotation.parsers import AnnotationParser
from wholeslidedata.annotation import utils as annotation_utils



class WholeSlideAnnotation():
    """
    This class contains all annotations of an image.
    """

    # fix for strtree segmentation fault bug
    STREE = {}

    def __init__(
        self,
        annotation_path,
        labels=None,
        renamed_labels=None,
        parser="asap",
        sort_by_overlay_index=False,
    ):
        self._annotation_path = Path(annotation_path)
        
        if not self._annotation_path.exists():
            raise FileNotFoundError(self._annotation_path)
        
        self._annotation_parser = AnnotationParser.create(parser)
        self._annotations = self._annotation_parser.read(annotation_path, labels, renamed_labels)

        self._sort_by_overlay_index = sort_by_overlay_index

        self._sampling_annotations = [
            annotation
            for annotation_type in self._annotation_parser.sample_annotation_types
            for annotation in self._annotations
            if isinstance(annotation, annotation_type)
        ]

        self._set_overlapping_annotations()
        WholeSlideAnnotation.STREE[self] = STRtree(self._annotations)

        self._labels = annotation_utils.get_labels_in_annotations(self.annotations)

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
    def sampling_annotations(self):
        return self._sampling_annotations

    def _set_overlapping_annotations(self):
        for annotation_index, annotation in enumerate(self._annotations[:-1]):
            if isinstance(annotation, Polygon):
                overlap_tree = STRtree(
                    annotation
                    for annotation in self._annotations[annotation_index + 1 :]
                )

                annotation.add_overlapping_annotations(overlap_tree.query(annotation))

    def select_annotations(self, center_x, center_y, width, height):
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
        return sorted(
            annotations,
            key=lambda item: self.labels.get_label_by_name(item.label.name).value,
        )
