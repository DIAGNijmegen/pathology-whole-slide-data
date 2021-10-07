from typing import Union
import numpy as np
from wholeslidedata.image.wholeslideimage import WholeSlideImage
from wholeslidedata.source.files import WholeSlideImageFile

class PatchSampler:
    def __init__(self, center=True, relative=False):
        self._center = center
        self._relative = relative

    def sample(self, image: Union[WholeSlideImage, WholeSlideImageFile], point, size, pixel_spacing):
        image_opened = isinstance(image, WholeSlideImage)

        if not image_opened:
            wsi = image.open()
        else:
            wsi = image

        patch = np.array(
            wsi.get_patch(
                point.x,
                point.y,
                *size,
                pixel_spacing,
                center=self._center,
                relative=self._relative,
            )
        )

        if not image_opened:
            wsi.close()
            wsi = None
            del wsi

        return patch.astype(np.uint8)





