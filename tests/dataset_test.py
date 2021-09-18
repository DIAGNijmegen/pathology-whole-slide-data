from wholeslidedata.source.files import WholeSlideAnnotationFile
from wholeslidedata.source.associations import associate_files
from wholeslidedata.source.utils import whole_slide_files_from_folder_factory
from wholeslidedata.dataset import WholeSlideDataSet
from .testdata import download, _WSI_NAME, _WSA_NAME
OUTPUT_FOLDER = '/tmp'
download(OUTPUT_FOLDER)


class TestDataSet:

    def test_dataset(self):
        image_files = whole_slide_files_from_folder_factory('/tmp/', 'wsi', excludes=('mask',), image_backend='openslide')
        annotation_files = whole_slide_files_from_folder_factory('/tmp/', 'wsa', excludes=('tif',), annotation_parser='asap')
        annotation_files.append(WholeSlideAnnotationFile(mode='default', path='dummy.xml', annotation_parser='asap'))
        associations = associate_files(image_files, annotation_files)
        dataset = WholeSlideDataSet(mode='default', associations=associations, labels=['lymphocytes'], copy_path='/tmp/data')
        assert dataset.annotation_counts == 3