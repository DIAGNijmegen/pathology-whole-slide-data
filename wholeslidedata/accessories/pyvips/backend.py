from typing import List, Tuple
import numpy as np
import pyvips

from wholeslidedata.image.backend import UnsupportedVendorError, WholeSlideImageBackend

@WholeSlideImageBackend.register(('pyvips', ))
class PyVipsImageBackend(WholeSlideImageBackend):
    def __init__(self, path: str) -> None:
        WholeSlideImageBackend.__init__(self, path)
        self._images = []
        self._images.append(pyvips.Image.openslideload(str(path), level=0))
        self._level_count = int(self._images[0].get('openslide.level-count'))
        for level in range(1, self._level_count):
            self._images.append(pyvips.Image.openslideload(str(path), level=level))
        self._regions = [pyvips.Region.new(image) for image in self._images]
        self._dowsamplings = self._init_downsamplings()

        
    def get_patch(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        level: int
    ) -> np.ndarray:
        image = self._regions[level]
        ratio =  self._dowsamplings[level]
        return np.array(image.fetch(int(x//ratio), int(y//ratio), int(width), int(height))).reshape(int(height), int(width), -1)[:, :, :3]
    
    def _init_shapes(self) -> List[Tuple[int, int]]:
        shapes= []
        for idx, image in enumerate(self._images):
            shapes.append((image.get(f'openslide.level[{idx}].width'),image.get(f'openslide.level[{idx}].height')))
        
        return shapes
            
    def _init_downsamplings(self) -> List[float]:
        downsamplings = []
        for idx, image in enumerate(self._images):
            downsamplings.append(float(image.get(f'openslide.level[{idx}].downsample')))
        return downsamplings
    
    def _init_spacings(self, downsamplings) -> List[float]:
        spacing = None
        try:
            spacing = float(self._images[0].get("openslide.mpp-x"))
        except:
            try:
                unit = {"cm": 10000, "centimeter": 10000}[
                    self._images[0].get("tiff.ResolutionUnit")
                ]
                res = float(self._images[0].get("tiff.XResolution"))
                spacing = unit / res
            except KeyError as key_error:
                raise UnsupportedVendorError(
                    self._path, self._images[0].get_fields()
                ) from key_error

        return [
            spacing * downsamplings[level]
            for level in range(self._level_count)
        ]

    def close(self):
        pass