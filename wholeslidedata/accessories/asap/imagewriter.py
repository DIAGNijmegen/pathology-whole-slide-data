import abc
from enum import Enum, auto
from pathlib import Path
from shutil import copyfile
from typing import List

import multiresolutionimageinterface as mir
import numpy as np
from multiresolutionimageinterface import MultiResolutionImageWriter
from shapely import geometry
from wholeslidedata.image.wholeslideimage import WholeSlideImage
from wholeslidedata.samplers.patchlabelsampler import SegmentationPatchLabelSampler


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
                self.writeBaseImagePartToLocation(
                    tile.flatten().astype("uint8"), col, row
                )
        else:
            self.writeBaseImagePart(tile.flatten().astype("uint8"))

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
    def __init__(self, callbacks=(), suffix=".tif"):
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
        self.setCompression(mir.Compression_LZW)
        self.setDataType(mir.DataType_UChar)
        self.setInterpolation(mir.Interpolation_NearestNeighbor)
        self.setColorType(mir.ColorType_Monochrome)

        # set writing spacing
        pixel_size_vec = mir.vector_double()
        pixel_size_vec.push_back(self._spacing)
        pixel_size_vec.push_back(self._spacing)
        self.setSpacing(pixel_size_vec)
        self.writeImageInformation(self._dimensions[0], self._dimensions[1])


class WholeSlideImageWriter(WholeSlideImageWriterBase):
    def __init__(self, callbacks=(), suffix=".tif"):
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
        self.setDataType(mir.DataType_UChar)
        self.setColorType(mir.ColorType_RGB)

        # set writing spacing
        pixel_size_vec = mir.vector_double()
        pixel_size_vec.push_back(self._spacing)
        pixel_size_vec.push_back(self._spacing)
        self.setSpacing(pixel_size_vec)
        self.writeImageInformation(self._dimensions[0], self._dimensions[1])


class MaskType(Enum):
    """Different mask types

    The PREDICTION type is for writing masks with prediction values, range=(0, num_classes)
    The HEATMAP type is for writing masks with heatmap values, range=(0, 255)
    """

    PREDICTION = auto()
    HEATMAP = auto()


class TmpWholeSlideMaskWriter(WholeSlideMaskWriter):
    def __init__(self, output_path: Path, callbacks=(), suffix=".tif"):
        """Writes temp file and copies the tmp file to an output folder in the save method.
        Args:
            output_path (Path): path to copy the writed file when saving.
        """

        self._output_path = output_path
        super().__init__(callbacks=callbacks, suffix=suffix)

    def save(self):
        super().save()
        self._copy_temp_path_to_output_path()

    def _copy_temp_path_to_output_path(self):
        print(f"Copying from: {self._path}")
        print(f"Copying to: {self._output_path}")
        copyfile(self._path, self._output_path)
        print("Removing tmp file...")
        Path(self._path).unlink()
        print(f"Copying done.")


def _create_writer(
    file: dict,
    output_folder: Path,
    tmp_folder: Path,
    real_spacing: float,
    shape: tuple,
    tile_size: int,
) -> TmpWholeSlideMaskWriter:
    """Creates a writer
    Args:
        file (dict): dictionary containing a 'name' and 'type' key.
        output_folder (Path): folder in where output should be copied
        tmp_folder (Path): folder in where output should be kept temporary when writing
        real_spacing (float): The spacing of the output file
        shape (tuple): The shape of the ouput file
    Raises:
        ValueError: raises when type in file is not valid
    Returns:
        TmpWholeSlideMaskWriter: a writer
    """

    if file["type"] == MaskType.HEATMAP:
        callbacks = (HeatmapTileCallback(heatmap_index=file["heatmap_index"]),)
    elif file["type"] == MaskType.PREDICTION:
        callbacks = (PredictionTileCallback(),)
    else:
        raise ValueError(f"Invalid file type: {file['type']}")

    writer = TmpWholeSlideMaskWriter(
        output_path=(output_folder / file["name"]), callbacks=callbacks
    )
    print(f'write: {(tmp_folder / file["name"])}')
    writer.write(
        path=(tmp_folder / file["name"]),
        spacing=real_spacing,
        dimensions=shape,
        tile_shape=(tile_size, tile_size),
    )
    return writer


def get_files(image_path, model_name, heatmaps):
    files = []
    # prediction
    prediction_file_name = image_path.stem + f"_{model_name}.tif"
    files.append({"name": prediction_file_name, "type": MaskType.PREDICTION})
    # heatmaps
    if heatmaps is not None:
        for value in heatmaps:
            heatmap_file_name = image_path.stem + f"_{model_name}_heat{value}.tif"
            files.append(
                {
                    "name": heatmap_file_name,
                    "type": MaskType.HEATMAP,
                    "heatmap_index": value,
                }
            )

    return files


def create_writers(
    image_path: Path,
    model_name: str,
    heatmaps: List[int],
    spacing: float,
    tile_size: int,
    output_folder: Path,
    tmp_folder: Path,
) -> list:

    """Creates writers
    Args:
        image_path (Path): path to the images that is being processed
        model_name (str): name of the model
        heatmaps (List): indices for heatmaps
        spacing: float:
        tile_sizeL int:
        output_folder (Path): folder in where output should be copied
        tmp_folder (Path): folder in where output should be kept temporary when writing
    Returns:
        list: the created writers
    """

    files = get_files(image_path=image_path, model_name=model_name, heatmaps=heatmaps)

    writers = []

    # get info
    with WholeSlideImage(image_path) as wsi:
        shape = wsi.shapes[wsi.get_level_from_spacing(spacing)]
        real_spacing = wsi.get_real_spacing(spacing)

    for file in files:
        if (output_folder / file["name"]).exists():
            f"Skipping prediction for {file['name']}, already exists in output folder: {output_folder}"
            continue

        writers.append(
            _create_writer(
                file=file,
                output_folder=output_folder,
                tmp_folder=tmp_folder,
                real_spacing=real_spacing,
                shape=shape,
                tile_size=tile_size,
            )
        )

    return writers


def write_mask(wsi, wsa, spacing, tile_size=1024, suffix="_gt_mask.tif"):
    shape = wsi.shapes[wsi.get_level_from_spacing(spacing)]
    ratio = wsi.get_downsampling_from_spacing(spacing)
    write_spacing = wsi.get_real_spacing(spacing)

    mask_output_path = str(wsa.path).replace(".xml", suffix)

    wsm_writer = WholeSlideMaskWriter()
    wsm_writer.write(
        path=mask_output_path,
        spacing=write_spacing,
        dimensions=(shape[0], shape[1]),
        tile_shape=(tile_size, tile_size),
    )

    label_sampler = SegmentationPatchLabelSampler()
    for y_pos in range(0, shape[1], tile_size):
        for x_pos in range(0, shape[0], tile_size):
            mask = label_sampler.sample(
                wsa,
                geometry.Point(
                    (x_pos + tile_size // 2) * ratio,
                    (y_pos + tile_size // 2) * ratio,
                ),
                (tile_size, tile_size),
                ratio,
            )
            if np.any(mask):
                wsm_writer.write_tile(tile=mask, coordinates=(int(x_pos), int(y_pos)))

    print("closing...")
    wsm_writer.save()
    print("done")
