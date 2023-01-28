from pathlib import Path
from wholeslidedata.image.wholeslideimage import WholeSlideImage
from wholeslidedata.interoperability.openslide.backend import (
    OpenSlideWholeSlideImageBackend,
)
from wholeslidedata.interoperability.asap.backend import AsapWholeSlideImageBackend
# from wholeslidedata.interoperability.pyvips.backend import PyVipsImageBackend
from wholeslidedata.interoperability.tiffslide.backend import TiffSlideImageBackend
import pytest


@pytest.fixture
def path():
    return Path("/tmp/TCGA-21-5784-01Z-00-DX1.tif")


def test_wsi_openslide(path):
    wsi = WholeSlideImage(path, backend=OpenSlideWholeSlideImageBackend)
    wsi.spacings
    wsi.shapes
    wsi.get_patch(0, 0, 64, 64, 8.0)


def test_wsi_asap(path):
    wsi = WholeSlideImage(path, backend=AsapWholeSlideImageBackend)
    wsi.spacings
    wsi.shapes
    wsi.get_patch(0, 0, 64, 64, 8.0)


def test_wsi_tiffslide(path):
    wsi = WholeSlideImage(path, backend=TiffSlideImageBackend)
    wsi.spacings
    wsi.shapes
    wsi.get_patch(0, 0, 64, 64, 8.0)


# def test_wsi_pyvips(path):
#     wsi = WholeSlideImage(path, backend=PyVipsImageBackend)
#     wsi.spacings
#     wsi.shapes
#     wsi.get_patch(512, 512, 64, 64, 8.0)


# def test_wsi_cucim(path):
#     wsi = WholeSlideImage(path, backend=CucimWholeSlideImageBackend)


