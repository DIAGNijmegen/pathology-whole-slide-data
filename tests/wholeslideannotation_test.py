import pytest
from typing import Union, Optional, List, Tuple, Dict
from wholeslidedata.annotation.wholeslideannotation import WholeSlideAnnotation
from wholeslidedata.annotation.types import Annotation
from wholeslidedata.labels import Labels
from pathlib import Path

class TestWholeSlideAnnotation:
    @pytest.fixture
    def annotation_path(self):
        return '/home/mart/Radboudumc/data/lung/TCGA-21-5784-01Z-00-DX1_E50E7F4B-BE37-4171-94A7-E824CFF4B3BB.xml'

    @pytest.fixture
    def labels(self):
        return ['stroma', 'tumor']

    @pytest.fixture
    def parser(self):
        return 'asap'

    @pytest.fixture
    def sort_by_overlay_index(self):
        return False

    @pytest.fixture
    def ignore_overlap(self):
        return True

    @pytest.fixture
    def wsa(self, annotation_path, labels, parser, sort_by_overlay_index, ignore_overlap):
        return WholeSlideAnnotation(annotation_path, labels, parser, sort_by_overlay_index, ignore_overlap)

    def test_path_property(self, wsa):
        assert isinstance(wsa.path, Path)

    def test_labels_property(self, wsa):
        assert isinstance(wsa.labels, Labels)