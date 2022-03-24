import os
import unittest
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("WebAgg")
from matplotlib import pyplot as plt
from shapely.geometry import Point
import sys

if sys.platform.startswith("win"):
    os.add_dll_directory(r"C:\Program Files\openslide-win64-20171122\bin")
    os.add_dll_directory(r"C:\Program Files\ASAP 2.0\bin")
    os.add_dll_directory(r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.2\bin")
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
        x_target = wsi.get_patch(x=15770, y=13260, width=284, height=284, spacing=0.5)
        x_context = wsi.get_patch(x=15770, y=13260, width=284, height=284, spacing=4.0)
        y_target = SegmentationPatchLabelSampler().sample(wsa, point=Point(15770, 13260), size=(284, 284), ratio=1)
        y_context = SegmentationPatchLabelSampler().sample(wsa, point=Point(15770, 13260), size=(284, 284), ratio=8)
        aug_x_batch, aug_y_batch = config_builder['wholeslidedata']['training']['batch_callbacks'][2](
            np.stack([x_target, x_context])[np.newaxis], np.stack([y_target, y_context])[np.newaxis]
        )

        self.plot_batch(aug_x_batch, aug_y_batch)

    @staticmethod
    def plot_batch(x_batch, y_batch, info=None):
        for s in range(x_batch.shape[0]):
            fig, axs = plt.subplots(2, 2, figsize=(10, 10))
            if info:
                x_coord, y_coord = info['sample_references'][0]['point'].xy
                plt.title(
                    f"Image: {info['sample_references'][0]['reference'].file_key}, Center point: {int(x_coord[-1])},{int(y_coord[-1])}")
            axs[0][0].imshow(x_batch[s][0].astype(np.int))
            axs[0][1].imshow(y_batch[s][0])
            axs[0][0].set_title(np.unique(y_batch[s][0]))
            axs[1][0].imshow(x_batch[s][1].astype(np.int))
            axs[1][1].imshow(y_batch[s][1])
            axs[1][0].set_title(np.unique(y_batch[s][0]))
            plt.tight_layout()
            plt.show()
