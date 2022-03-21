import os
import sys
import wholeslidedata

if sys.platform.startswith("win"):
    os.add_dll_directory(r"C:\Program Files\ASAP 2.0\bin")

import unittest
from pathlib import Path

from shapely.geometry import Point

from tests.testdata import download_wsi, download_wsa
from wholeslidedata.configuration.config import WholeSlideDataConfiguration
from wholeslidedata.samplers.utils import plot_patch, plot_mask
from wholeslidedata.source.utils import whole_slide_files_from_folder_factory


class TestsConfigurations(unittest.TestCase):

    def test_albumentation_callback(self):
        test_files = os.path.dirname(__file__) / Path("test_files")
        download_wsi(test_files)
        download_wsa(test_files)
        config_file = os.path.join(str(test_files.absolute()), "user_config.yml")

        config_builder = WholeSlideDataConfiguration.build(user_config=config_file, modes=("training",))

        wsi = whole_slide_files_from_folder_factory(test_files, 'wsi', excludes=('mask',), image_backend='asap')[0]
        wsa = whole_slide_files_from_folder_factory(test_files, 'wsa', annotation_parser='asap')[0]
        x_samples, y_samples = config_builder['wholeslidedata']['training']['sample_sampler'].sample(wsi.open(),
                                                                                                     wsa.open(),
                                                                                                     point=Point(15770,
                                                                                                                 13260))
        x = x_samples[.5][(284, 284, 3)]
        y = y_samples[.5][(284, 284, 3)]
        aug_x, aug_y = config_builder['wholeslidedata']['training']['sample_callbacks'][1](x, y)
        plot_patch(x)
        plot_patch(aug_x)
        plot_mask(y)
        plot_mask(aug_y)
