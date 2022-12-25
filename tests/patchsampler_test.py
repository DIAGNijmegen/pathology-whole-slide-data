import pytest

from wholeslidedata.samplers.patchsampler import PatchSampler
from shapely.geometry import Point
from wholeslidedata.image.wholeslideimage import WholeSlideImage
from wholeslidedata.files import WholeSlideImageFile

image_path  = "/home/mart/Radboudumc/data/lung/TCGA-21-5784-01Z-00-DX1_E50E7F4B-BE37-4171-94A7-E824CFF4B3BB.tif"

@pytest.fixture
def image():
    return WholeSlideImage(image_path)

@pytest.fixture
def image_file():
    return WholeSlideImageFile('train', image_path, image_backend='openslide')


@pytest.fixture
def point():
    return Point(500,500)

def test_init():
    ps = PatchSampler()
    assert ps._center == True
    assert ps._relative == False

    ps = PatchSampler(center=False, relative=True)
    assert ps._center == False
    assert ps._relative == True

def test_sample(image, image_file, point):
    size = (64, 64)

    ps = PatchSampler()
    patch, ratio = ps.sample(image, point, size, 0.5)
    assert int(ratio) == 1
    assert patch.shape == size + (3,)
    
    ps = PatchSampler(center=False, relative=True)
    patch, ratio = ps.sample(image_file, point, size, 1.0)
    assert int(ratio) == 2
    assert patch.shape == size + (3,)
    