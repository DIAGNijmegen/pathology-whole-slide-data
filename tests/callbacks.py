import os
import unittest
from pathlib import Path

import numpy as np
from shapely.geometry import Point

from tests.testdata import download_wsi, download_wsa
from wholeslidedata.configuration.config import WholeSlideDataConfiguration
from wholeslidedata.samplers.patchlabelsampler import SegmentationPatchLabelSampler
from wholeslidedata.samplers.utils import plot_patch, plot_mask
from wholeslidedata.source.utils import whole_slide_files_from_folder_factory


class TestsConfigurations(unittest.TestCase):

    def test_albumentation_callback(self):
        test_files = os.path.dirname(__file__) / Path("test_files")
        download_wsi(test_files)
        download_wsa(test_files)
        config_file = os.path.join(str(test_files.absolute()), "user_config.yml")

        config_builder = WholeSlideDataConfiguration.build(user_config=config_file, modes=("training",))

        wsi = whole_slide_files_from_folder_factory(test_files, 'wsi', excludes=('mask',), image_backend='openslide')[
            0].open()
        wsa = whole_slide_files_from_folder_factory(test_files, 'wsa', annotation_parser='asap')[0].open()
        x = wsi.get_patch(x=15770, y=13260, width=284, height=284, spacing=0.5)
        y = SegmentationPatchLabelSampler().sample(wsa, point=Point(15770, 13260), size=(284, 284), ratio=1)
        aug_x, aug_y = config_builder['wholeslidedata']['training']['sample_callbacks'][1](x, y)

        print(x.mean(), aug_x.mean())

        plot_patch(x)
        plot_patch(aug_x)
        plot_mask(y)
        plot_mask(aug_y)
