
from wholeslidedata.dataset import WholeSlideDataSet
import pytest

@pytest.fixture
def associations():
    # Set up dataset
    pass


# def test_init(dataset):
#     # wsd = WholeSlideDataSet(mode='train', associations=associations, labels=labels)
#     assert dataset.mode == 'train'
#     assert dataset.associations == associations
#     assert dataset.labels == labels

# def test__open(associations, labels):
#     wsd = WholeSlideDataSet(mode='train', associations=associations, labels=labels)
#     data = wsd._open(associations, labels)
#     # Assert that data is a dictionary with the expected keys and values

# def test__open_image(associations, labels):
#     wsd = WholeSlideDataSet(mode='train', associations=associations, labels=labels)
#     wsi_file = WholeSlideImageFile(...)
#     image = wsd._open_image(wsi_file)
#     # Assert that image is the expected object

# def test__open_annotation(associations, labels):
#     wsd = WholeSlideDataSet(mode='train', associations=associations, labels=labels)
#     wsa_file = WholeSlideAnnotationFile(...)
#     annotation = wsd._open_annotation(wsa_file, labels)
#     # Assert that annotation is the expected object

# def test__init_labels(associations, labels):
#     wsd = WholeSlideDataSet(mode='train', associations=associations, labels=labels)
#     wsd._data = {...}  # Set up test data
#     init_labels = wsd._init_labels()
#     # Assert that init_labels is the expected object

# def test__init_samples(associations, labels):
#     wsd = WholeSlideDataSet(mode='train', associations=associations, labels=labels)
#     wsd._data = {...}  # Set up test data
#     sample_references = wsd._init_samples()
#     # Assert that sample_references is the expected object

# def test_close_images(associations, labels):
#     wsd = WholeSlideDataSet(mode='train', associations=associations, labels=labels)
#     wsd._images = {...}  # Set up test data
#     wsd.close_images()
#     # Assert that wsd._images is an empty dictionary

# def test_annotation_counts(associations, labels):
#     wsd = WholeSlideDataSet(mode='train', associations=associations, labels=labels)
#     wsd._data = {...}  # Set up test data
#     annotation_counts = wsd.annotation_counts
#     # Assert that annotation

# def test_annotations_per_label(associations, labels):
#     wsd = WholeSlideDataSet(mode='train', associations=associations, labels=labels)
#     wsd._data = {...}  # Set up test data
#     annotations_per_label = wsd.annotations_per_label
#     # Assert that annotations_per_label is the expected dictionary

# def test_labels(associations, labels):
#     wsd = WholeSlideDataSet(mode='train', associations=associations, labels=labels)
#     wsd._data = {...}  # Set up test data
#     wsd._labels = [...}  # Set up test labels
#     labels_ = wsd.labels
#     # Assert that labels_ is the expected object

# def test_samples(associations, labels):
#     wsd = WholeSlideDataSet(mode='train', associations=associations, labels=labels)
#     wsd._data = {...}  # Set up test data
#     wsd._sample_references = {...}  # Set up test sample references
#     samples = wsd.samples
#     # Assert that samples is the expected object

# def test_get_image(associations, labels):
#     wsd = WholeSlideDataSet(mode='train', associations=associations, labels=labels)
#     wsd._data = {...}  # Set up test data
#     image = wsd.get_image(file_index=0, wsi_index=0)
#     # Assert that image is the expected object

# def test_get_annotation(associations, labels):
#     wsd = WholeSlideDataSet(mode='train', associations=associations, labels=labels)
#     wsd._data = {...}  # Set up test data
#     annotation = wsd.get_annotation(file_index=0, wsa_index=0)
#     # Assert that annotation is the expected object

# def test_get_sample(associations, labels):
#     wsd = WholeSlideDataSet(mode='train', associations=associations, labels=labels)
#     wsd._data = {...}  # Set up test data
#     wsd._sample_references = {...}  # Set up test sample references
#     sample = wsd.get_sample(label_name='label1', sample_index=0)
#     # Assert that sample is the expected object