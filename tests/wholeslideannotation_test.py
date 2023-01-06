from pathlib import Path

import pytest

from wholeslidedata.annotation.wsa import WholeSlideAnnotation
from wholeslidedata.interoperability.asap.parser import AsapAnnotationParser
from wholeslidedata.annotation.labels import Labels
from wholeslidedata.annotation.hooks import ScalingAnnotationHook, TiledAnnotationHook

from .downloaddata import download_annotation_data, download_example_data


class TestWholeSlideAnnotation:
    @pytest.fixture
    def annotation_path(self):
        return download_annotation_data()

    @pytest.fixture
    def wsa(self, annotation_path):
        return WholeSlideAnnotation(annotation_path)

    def test_parser_initializations(self, annotation_path):
        WholeSlideAnnotation(annotation_path)
        WholeSlideAnnotation(annotation_path, parser=AsapAnnotationParser)
        WholeSlideAnnotation(annotation_path, parser=AsapAnnotationParser())

    def test_path_property(self, wsa, annotation_path):
        assert isinstance(wsa.path, Path) and wsa.path == annotation_path

    def test_labels_property(self, wsa):
        assert isinstance(wsa.labels, Labels)
        label_names = set([label.name for label in wsa.labels])
        assert label_names == set(["tumor", "stroma", "lymphocytes"])

    def test_rename_labels(self, annotation_path):
        wsa = WholeSlideAnnotation(annotation_path, labels={'tumor':1, 'stroma': 2, 'lymphocytes': 2}, renamed_labels={'tumor':1, 'other': 2})
        assert isinstance(wsa.labels, Labels)
        label_names = set([label.name for label in wsa.labels])
        assert label_names == set(["tumor", "other"])

    def test_sampling_annotations(self, annotation_path):
        wsa = WholeSlideAnnotation(annotation_path, sample_label_names=["tumor"])
        label_names = set(
            [label_name for label_name in wsa.sampling_annotations_per_label]
        )
        assert label_names == set(["tumor"])

    def test_annotation_per_label(self, wsa):
        assert set(wsa.annotations_per_label) == set(["tumor", "stroma", "lymphocytes"])

    def test_select_annotations(self,wsa: WholeSlideAnnotation):
        annotations = wsa.select_annotations(7500, 15000, 5000, 10000)
        assert len(annotations) == 5
        assert set(['tumor']) == set([annotation.label.name for annotation in annotations])

    def test_overlapping_annotations(self, annotation_path):
        wsa = WholeSlideAnnotation(annotation_path, sample_label_names=["tumor"], ignore_overlap=False)

    def test_scaling_hook(self, wsa: WholeSlideAnnotation, annotation_path):
        wsa_scaled = WholeSlideAnnotation(annotation_path, sample_label_names=["tumor"], hooks=(ScalingAnnotationHook(0.5),))
        assert wsa.annotations[0].coordinates[0][0]/2 == wsa_scaled.annotations[0].coordinates[0][0]

    def test_tiled_hook(self, annotation_path):
        wsa_tiled = WholeSlideAnnotation(annotation_path, sample_label_names=["tumor"], hooks=(TiledAnnotationHook(tile_size=64, label_names=['tumor']),))
        assert wsa_tiled.sampling_annotations[0].size == (64,64)