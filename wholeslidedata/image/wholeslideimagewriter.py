import abc

from pathlib import Path


import multiresolutionimageinterface as mir
import numpy as np



class AsapNotFoundError(ImportError):
    ...


try:
    from multiresolutionimageinterface import MultiResolutionImageWriter
except ImportError:
    raise AsapNotFoundError('can not find installed asap for wholeslideimage writing')


class TileShapeError(Exception):
    pass


class CoordinateError(Exception):
    pass


class InvalidWriterError(Exception):
    pass


class TileCallback:
    @abc.abstractmethod
    def __call__(self, tile):
        pass


class HeatmapTileCallback(TileCallback):
    def __init__(self, heatmap_index, multiplier=255):
        self._heatmap_index = heatmap_index
        self._multiplier = multiplier

    def __call__(self, tile):
        return tile[..., self._heatmap_index] * self._multiplier


class PredictionTileCallback(TileCallback):
    def __init__(self, offset=1):
        self._offset = offset

    def __call__(self, tile):
        return np.argmax(tile, -1) + self._offset


class Writer(abc.ABC):
    def __init__(self, callbacks=None):
        self._callbacks = callbacks


class WholeSlideImageWriterBase(Writer, MultiResolutionImageWriter):
    def __init__(self, callbacks=()):
        Writer.__init__(self, callbacks)
        MultiResolutionImageWriter.__init__(self)

    def write_tile(self, tile, coordinates=None, mask=None):
        tile = self._apply_tile_callbacks(tile)
        tile = self._mask_tile(tile, mask)
        tile = self._crop_tile(tile)
        self._write_tile_to_image(tile, coordinates)

    def _write_tile_to_image(self, tile, coordinates):
        if coordinates:
            col, row = self._get_col_row(coordinates)
            if col is not None and row is not None:
                self.writeBaseImagePartToLocation(tile.flatten().astype('uint8'), col, row)
        else:
            self.writeBaseImagePart(tile.flatten().astype('uint8'))

    def _get_col_row(self, coordinates):
        x, y = coordinates
        if x < self._dimensions[0] and x >= 0 and y < self._dimensions[1] and y >= 0:
            return x, y

        return None, None
        raise CoordinateError(
            f"Invalid coordinate x,y={x, y} with dimension setting {self._dimensions}"
        )

    def _apply_tile_callbacks(self, tile):
        for callback in self._callbacks:
            tile = callback(tile)
        return tile

    def _mask_tile(self, tile, mask):
        if mask is not None:
            tile = tile.reshape(mask.shape[:2])
            tile *= mask
        return tile

    def _crop_tile(self, tile):
        if len(tile.shape) == 2:
            return tile[: self._tile_shape[1], : self._tile_shape[0]]

        if len(tile.shape) == 3:
            return tile[: self._tile_shape[1], : self._tile_shape[0], :]

        raise TileShapeError(
            f"Invalid tile shape: {tile.shape}, tile shape should contain at 2 or 3 dimensions"
        )

    def save(self):
        self.finishImage()


class WholeSlideMaskWriter(WholeSlideImageWriterBase):
    def __init__(self, callbacks=(), suffix='.tif'):
        super().__init__(callbacks=callbacks)
        self._suffix = suffix

    def write(self, path, spacing, dimensions, tile_shape):
        self._path = str(path).replace(Path(path).suffix, self._suffix)
        self._spacing = spacing
        self._dimensions = dimensions
        self._tile_shape = tile_shape

        print(f"Creating: {self._path}....")
        print(f"Spacing: {self._spacing}")
        print(f"Dimensions: {self._dimensions}")
        print(f"Tile_shape: {self._tile_shape}")

        self.openFile(self._path)
        self.setTileSize(self._tile_shape[0])
        self.setCompression(mir.LZW)
        self.setDataType(mir.UChar)
        self.setInterpolation(mir.NearestNeighbor)
        self.setColorType(mir.Monochrome)

        # set writing spacing
        pixel_size_vec = mir.vector_double()
        pixel_size_vec.push_back(self._spacing)
        pixel_size_vec.push_back(self._spacing)
        self.setSpacing(pixel_size_vec)
        self.writeImageInformation(self._dimensions[0], self._dimensions[1])

class WholeSlideImageWriter(WholeSlideImageWriterBase):
    def __init__(self, callbacks=(), suffix='.tif'):
        super().__init__(callbacks=callbacks)
        self._suffix = suffix

    def write(self, path, spacing, dimensions, tile_shape, jpeg_quality=80):
        self._path = str(path).replace(Path(path).suffix, self._suffix)
        self._spacing = spacing
        self._dimensions = dimensions
        self._tile_shape = tile_shape

        print(f"Creating: {self._path}....")
        print(f"Spacing: {self._spacing}")
        print(f"Dimensions: {self._dimensions}")
        print(f"Tile_shape: {self._tile_shape}")

        self.openFile(self._path)
        self.setTileSize(self._tile_shape[0])
        self.setJPEGQuality(jpeg_quality)
        self.setDataType(mir.UChar)
        self.setColorType(mir.RGB)

        # set writing spacing
        pixel_size_vec = mir.vector_double()
        pixel_size_vec.push_back(self._spacing)
        pixel_size_vec.push_back(self._spacing)
        self.setSpacing(pixel_size_vec)
        self.writeImageInformation(self._dimensions[0], self._dimensions[1])


  