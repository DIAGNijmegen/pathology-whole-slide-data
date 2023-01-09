import numpy as np

from wholeslidedata.annotation.types import Annotation
from wholeslidedata.annotation.wholeslideannotation import WholeSlideAnnotation
from wholeslidedata.image.wholeslideimage import WholeSlideImage
from wholeslidedata.interoperability.albumentations.callbacks import (
    AlbumentationsSegmentationBatchCallback,
)
from wholeslidedata.interoperability.asap.backend import AsapWholeSlideImageBackend
from wholeslidedata.samplers.patchlabelsampler import SegmentationPatchLabelSampler

augmentations = [
    {
        "RandomRotate90": {"p": 0.5},
        "Flip": {"p": 0.5},
        "RandomSizedCrop": {
            "p": 1,
            "min_max_height": [100, 200],
            "height": 284,
            "width": 284,
        },
        "ElasticTransform": {
            "p": 0.5,
            "alpha": 45,
            "sigma": 6,
            "alpha_affine": 4,
        },
        "HueSaturationValue": {
            "hue_shift_limit": 0.2,
            "sat_shift_limit": 0.3,
            "val_shift_limit": 0.2,
            "p": 0.5,
        },
        "GridDistortion": {"p": 1.0},
        "RandomBrightnessContrast": {"p": 0.4},
    }
]


def test_albumentation_callback():
    wsi = WholeSlideImage(
        "/tmp/TCGA-21-5784-01Z-00-DX1.tif", backend=AsapWholeSlideImageBackend
    )
    wsa = WholeSlideAnnotation("/tmp/TCGA-21-5784-01Z-00-DX1.xml")
    point = Annotation.create(1, {"name": "p", "value": 1}, (15770, 13260))
    aug = AlbumentationsSegmentationBatchCallback(augmentations=augmentations)
    x_target = wsi.get_patch(x=15770, y=13260, width=284, height=284, spacing=0.5)
    x_context = wsi.get_patch(x=15770, y=13260, width=284, height=284, spacing=4.0)
    y_target = SegmentationPatchLabelSampler().sample(
        wsa, point=point.geometry, size=(284, 284), ratio=1
    )
    y_context = SegmentationPatchLabelSampler().sample(
        wsa, point=point.geometry, size=(284, 284), ratio=8
    )
    aug_x_batch, aug_y_batch = aug(
        np.stack([x_target, x_context])[np.newaxis],
        np.stack([y_target, y_context])[np.newaxis],
    )
    aug_x_batch, aug_y_batch = aug(np.array([x_target]), np.array([y_target]))
