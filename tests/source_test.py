from wholeslidedata.source.utils import whole_slide_files_from_folder_factory
from .testdata import download, _WSI_NAME, _WSA_NAME
OUTPUT_FOLDER = '/tmp'
download(OUTPUT_FOLDER)

class TestSource:
    
    def test_whole_slide_files_from_folder_factory_asap(self):
        image_files = whole_slide_files_from_folder_factory(OUTPUT_FOLDER, 'wsi', excludes=('mask',), image_backend='asap')
        annotation_files = whole_slide_files_from_folder_factory(OUTPUT_FOLDER, 'wsa', annotation_parser='asap')

        assert image_files[0].path == OUTPUT_FOLDER / _WSI_NAME
        assert annotation_files[0].path == OUTPUT_FOLDER / _WSA_NAME


