from wholeslidedata.source.utils import whole_slide_files_from_folder_factory
from .testdata import download, _WSI_NAME, _WSA_NAME
OUTPUT_FOLDER = '/tmp'
download(OUTPUT_FOLDER)


class TestImage:


    def test_wholeslide_image_asap(self):
        image_files = whole_slide_files_from_folder_factory(OUTPUT_FOLDER, 'wsi', excludes=('mask',), image_backend='asap')


        wsi = image_files[0].open()
        assert wsi.spacings == [0.5054008297457606,
                                 1.0108291327955978,
                                 2.021767917813607,
                                 4.043535835627214,
                                 8.087071671254428,
                                 16.181168796547833,
                                 32.390481824177165]

    def test_wholeslide_image_openslide(self):
        image_files = whole_slide_files_from_folder_factory(OUTPUT_FOLDER, 'wsi', excludes=('mask',), image_backend='openslide')


        wsi = image_files[0].open()
        assert wsi.spacings == [0.5054008216842545,
                                1.0108352937951,
                                2.0217254523901094,
                                4.043450904780219,
                                8.088178124603436,
                                16.179869312415683,
                                32.373809206692044]