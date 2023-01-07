from wholeslidedata.samplers.patchlabelsampler import (
    MaskPatchLabelSampler,
    ClassificationPatchLabelSampler,
    DetectionPatchLabelSampler,
    SegmentationPatchLabelSampler,
)
from wholeslidedata.interoperability.asap.backend import AsapWholeSlideImageBackend
from wholeslidedata.annotation.wholeslideannotation import WholeSlideAnnotation
from shapely.geometry import Point
import numpy as np


def test_mask_patch_label_sampler_test():
    wsa = WholeSlideAnnotation("/tmp/TCGA-21-5784-01Z-00-DX1_tb_mask.tif")
    label_sampler = MaskPatchLabelSampler(
        image_backend=AsapWholeSlideImageBackend,
        ratio=4,
        center=True,
        relative=False,
        spacing=2.0,
    )
    p = Point(wsa.annotations[60].center)
    label_patch = label_sampler.sample(wsa, p, (1024, 1024), 1)
    assert np.unique(label_patch) == [1]


def test_classification_label_sampler_test():
    label_map = {"tumor": 1, "stroma": 2, "lymphocytes": 3}
    wsa = WholeSlideAnnotation("/tmp/TCGA-21-5784-01Z-00-DX1.xml", labels=label_map)
    label_sampler = ClassificationPatchLabelSampler()
    p = Point(wsa.annotations[0].center)
    label_value = wsa.annotations[0].label.value
    label = label_sampler.sample(wsa, p, (1024, 1024), 1)
    assert label[0] == label_value


def test_detection_label_sampler_test():
    label_map = {"tumor": 1}
    wsa = WholeSlideAnnotation("/tmp/TCGA-21-5784-01Z-00-DX1.xml", labels=label_map)
    label_sampler = DetectionPatchLabelSampler(
        max_number_objects=10, detection_labels=["tumor"]
    )
    p = Point(wsa.annotations[0].center)
    detections = label_sampler.sample(wsa, p, (1024, 1024), 1)
    assert len(detections) == 10


def test_segmentation_label_sampler_test():
    label_map = {"tumor": 1}
    wsa = WholeSlideAnnotation("/tmp/TCGA-21-5784-01Z-00-DX1.xml", labels=label_map)
    label_sampler = SegmentationPatchLabelSampler()
    p = Point(wsa.annotations[0].center)
    mask = label_sampler.sample(wsa, p, (1024, 1024), 1)
    assert mask.shape == (1024, 1024)
