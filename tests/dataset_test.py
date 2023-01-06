
from pathlib import Path
from wholeslidedata.annotation.types import Annotation
from wholeslidedata.image.wsi import WholeSlideImage
from wholeslidedata.source.dataset import WholeSlideDataSet
from sourcelib.collect import get_files_from_folder
from sourcelib.associations import associate_files
from wholeslidedata.source.files import WholeSlideImageFile, WholeSlideAnnotationFile
from wholeslidedata.source.mode import WholeSlideMode
from wholeslidedata.interoperability.asap.backend import AsapWholeSlideImageBackend
from wholeslidedata.interoperability.asap.parser import AsapAnnotationParser
import pytest
from .downloaddata import download_example_data

@pytest.fixture
def associations():
    download_example_data()
    image_files =get_files_from_folder(file_cls=WholeSlideImageFile, folder='/tmp/', mode=WholeSlideMode.training, excludes=['mask'], image_backend=AsapWholeSlideImageBackend)
    annotation_files =get_files_from_folder(file_cls=WholeSlideAnnotationFile, folder='/tmp/', mode=WholeSlideMode.training, filters=['xml'], annotation_parser=AsapAnnotationParser)
    return associate_files(image_files, annotation_files)

@pytest.fixture
def dataset(associations):
    return WholeSlideDataSet(mode=WholeSlideMode.training, associations=associations)

def test_dataset_data(dataset):
    assert len(list(dataset.keys())) == 1
    assert "TCGA-21-5784-01Z-00-DX1" in list(dataset.keys())

def test_dataset_labels(dataset):
    assert len(dataset.sample_labels) == 3
    assert set(dataset.sample_labels.names) == set(['tumor', 'stroma', 'lymphocytes'])

def test_dataset_mode(dataset):
    assert dataset.mode == WholeSlideMode.training

def test_dataset_load_images(associations):
    dataset =  WholeSlideDataSet(mode=WholeSlideMode.training, associations=associations, load_images=True)
    assert isinstance(dataset.get_wsi_from_reference(dataset.sample_references['tumor'][0]), WholeSlideImage)

    dataset =  WholeSlideDataSet(mode=WholeSlideMode.training, associations=associations, load_images=False)
    assert isinstance(dataset.get_wsi_from_reference(dataset.sample_references['tumor'][0]), WholeSlideImageFile)

def test_copy(associations):
    _ = WholeSlideDataSet(mode=WholeSlideMode.training, associations=associations, load_images=True, copy_path="/tmp/copy")
    assert Path('/tmp/copy/images/TCGA-21-5784-01Z-00-DX1.tif').exists()
    assert Path('/tmp/copy/annotations/TCGA-21-5784-01Z-00-DX1.xml').exists() 
    Path('/tmp/copy/images/TCGA-21-5784-01Z-00-DX1.tif').unlink()
    Path('/tmp/copy/annotations/TCGA-21-5784-01Z-00-DX1.xml').unlink()

def test_get_wsi(dataset):
    assert dataset.get_wsi_from_reference(dataset.sample_references['tumor'][0]).path.name == "TCGA-21-5784-01Z-00-DX1.tif"

def test_get_wsa(dataset):
    assert dataset.get_wsa_from_reference(dataset.sample_references['tumor'][0]).path.name == "TCGA-21-5784-01Z-00-DX1.xml"

def test_get_annotation(dataset):
    assert isinstance(dataset.get_annotation_from_reference(dataset.sample_references['tumor'][0]), Annotation)

def test_annotation_counts(dataset):
    assert dataset.annotation_counts == 10

def test_annotations_per_label(dataset):
    for key, value in dataset.annotations_per_label.items():
        assert key in ['tumor', 'stroma', 'lymphocytes']
        if key == 'tumor':
            assert value == 5
        if key == 'stroma':
            assert value == 2
        if key == 'lymphocytes':
            assert value == 3

def test_annnotations_per_key(dataset: WholeSlideDataSet):
    assert dataset.annotations_per_key['TCGA-21-5784-01Z-00-DX1'] == 10 

def test_annotations_per_label_per_key(dataset: WholeSlideDataSet):
    for key, value in dataset.annotations_per_label_per_key['TCGA-21-5784-01Z-00-DX1'].items():
        assert key in ['tumor', 'stroma', 'lymphocytes']
        if key == 'tumor':
            assert value == 5
        if key == 'stroma':
            assert value == 2
        if key == 'lymphocytes':
            assert value == 3

def test_pixel_count(dataset: WholeSlideDataSet):
    assert dataset.pixels_count == 2016854
                                     

def test_pixels_per_label(dataset: WholeSlideDataSet):
    for key, value in dataset.pixels_per_label.items():
        assert key in ['tumor', 'stroma', 'lymphocytes']
        if key == 'tumor':
            assert value == 1303963
        if key == 'stroma':
            assert value == 155316
        if key == 'lymphocytes':
            assert value == 557575

def test_pixels_per_key(dataset: WholeSlideDataSet):
    assert dataset.pixels_per_key["TCGA-21-5784-01Z-00-DX1"] == 2016854

def test_pixels_per_label_per_key(dataset: WholeSlideDataSet):
    for key, value in dataset.pixels_per_label_per_key["TCGA-21-5784-01Z-00-DX1"].items():
        assert key in ['tumor', 'stroma', 'lymphocytes']
        if key == 'tumor':
            assert value == 1303963
        if key == 'stroma':
            assert value == 155316
        if key == 'lymphocytes':
            assert value == 557575

