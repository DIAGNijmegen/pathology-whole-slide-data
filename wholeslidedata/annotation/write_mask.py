from wholeslidedata.image.wholeslideimagewriter import WholeSlideMaskWriter
from wholeslidedata.samplers.patchlabelsampler import SegmentationPatchLabelSampler
from shapely.geometry import Point as ShapelyPoint
import numpy as np


def write_mask(wsi, wsa, spacing, tile_size=1024, suffix='_gt_mask.tif'):
    shape = wsi.shapes[wsi.get_level_from_spacing(spacing)]
    ratio = wsi.get_downsampling_from_spacing(spacing)
    write_spacing = wsi.get_real_spacing(spacing)

    mask_output_path = str(wsa.path).replace('.xml', suffix)
        
    wsm_writer = WholeSlideMaskWriter()
    wsm_writer.write(path=mask_output_path, spacing=write_spacing, dimensions=(shape[0], shape[1]), tile_shape=(tile_size,tile_size))

    
    label_sampler = SegmentationPatchLabelSampler()
    for y_pos in range(0, shape[1], tile_size):
        for x_pos in range(0, shape[0], tile_size):
            mask = label_sampler.sample(
                wsa,
                ShapelyPoint(
                    (x_pos + tile_size // 2) * ratio,
                    (y_pos + tile_size // 2) * ratio,
                ),
                (tile_size, tile_size),
                ratio,
            )
            if np.any(mask):
                wsm_writer.write_tile(tile=mask,coordinates=(int(x_pos),int(y_pos)))

    print("closing...")
    wsm_writer.save()
    print("done")