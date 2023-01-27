import pytest
from pathlib import Path
from typing import Union, List, Tuple
from wholeslidedata.image.wholeslideimage import WholeSlideImage
from wholeslidedata.annotation.types import Annotation
import numpy as np
from wholeslidedata.annotation.labels import Label
from wholeslidedata.interoperability.openslide.backend import (
    OpenSlideWholeSlideImageBackend,
)


class TestWholeSlideImage:
    @pytest.fixture
    def wsi(self):
        path = Path(
            "/home/mart/Radboudumc/data/lung/TCGA-21-5784-01Z-00-DX1_E50E7F4B-BE37-4171-94A7-E824CFF4B3BB.tif"
        )
        return WholeSlideImage(path, backend=OpenSlideWholeSlideImageBackend)

    def test_path_property(self, wsi):
        assert wsi.path == Path(
            "/home/mart/Radboudumc/data/lung/TCGA-21-5784-01Z-00-DX1_E50E7F4B-BE37-4171-94A7-E824CFF4B3BB.tif"
        )

    def test_spacings_property(self, wsi):
        assert len(wsi.spacings) > 0

    def test_shapes_property(self, wsi):
        assert len(wsi.shapes) > 0

    def test_downsamplings_property(self, wsi):
        assert len(wsi.downsamplings) > 0

    def test_get_downsampling_from_level(self, wsi):
        level = 0
        assert isinstance(wsi.get_downsampling_from_level(level), float)

    def test_get_level_from_spacing(self, wsi):
        spacing = 0.5
        assert isinstance(wsi.get_level_from_spacing(spacing), int)

    def test_get_real_spacing(self, wsi):
        spacing = 0.5
        assert isinstance(wsi.get_real_spacing(spacing), float)

    def test_get_slide(self, wsi):
        spacing = 2.0
        assert isinstance(wsi.get_slide(spacing), np.ndarray)

    def test_get_region(self, wsi: WholeSlideImage):
        annotation = Annotation.create(
            index=0,
            label=Label("label1", 1),
            coordinates=np.array([[0, 0], [1, 1], [2, 5], [1, 1]]),
        )
        spacing = 0.5
        margin = 0
        masked = True
        assert isinstance(
            wsi.get_region_from_annotations([annotation], spacing, margin, masked), np.ndarray
        )

    def test_get_downsampling_from_spacing(self, wsi):
        spacing = 0.5
        assert isinstance(wsi.get_downsampling_from_spacing(spacing), float)

    def test_get_shape_from_spacing(self, wsi):
        spacing = 0.5
        assert isinstance(wsi.get_shape_from_spacing(spacing), tuple)

    def test_get_patch(self, wsi):
        x = 0
        y = 0
        width = 100
        height = 100
        spacing = 0.3
        center = False
        assert isinstance(
            wsi.get_patch(x, y, width, height, spacing, center), np.ndarray
        )

    def test_enter_exit(self, wsi):
        with WholeSlideImage(
            "/home/mart/Radboudumc/data/lung/TCGA-21-5784-01Z-00-DX1_E50E7F4B-BE37-4171-94A7-E824CFF4B3BB.tif",
            backend=OpenSlideWholeSlideImageBackend,
        ) as slide:
            assert isinstance(slide, WholeSlideImage)
