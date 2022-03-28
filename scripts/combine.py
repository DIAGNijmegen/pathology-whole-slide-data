from wholeslidedata.image.wholeslideimage import WholeSlideImage
from wholeslidedata.accessories.asap.imagewriter import WholeSlideMaskWriter
from wholeslidedata.annotation.parser import MaskAnnotationParser
from wholeslidedata.accessories.asap.annotationwriter import write_asap_annotation
from shapely.ops import unary_union
import click
from pathlib import Path
from matplotlib import pyplot as plt
import time 


@click.command()
@click.option("--tumor_mask", type=Path, required=True)
@click.option("--tissue_mask", type=Path, required=True)
@click.option("--mask_output", type=Path, required=True)
@click.option("--xml_output", type=Path, required=True)
def main(tumor_mask, tissue_mask, mask_output, xml_output):
    tumor_mask = WholeSlideImage(tumor_mask, backend='asap')
    tissue_mask = WholeSlideImage(tissue_mask, backend='asap')
    spacing = 2.0
    tile_size = 512
    tumor_slide = tumor_mask.get_slide(spacing)
    tissue_slide = tissue_mask.get_slide(spacing)
    tissue_slide[tumor_slide==1] = 0
    wsm_writer = WholeSlideMaskWriter()
    shape = tissue_mask.shapes[tissue_mask.get_level_from_spacing(spacing)]
    wsm_writer.write(mask_output, spacing=tissue_mask.get_real_spacing(spacing), dimensions=shape, tile_shape=(tile_size, tile_size))
    for row in range(0, shape[1], tile_size):
        for col in range(0, shape[0], tile_size):
            tile = tissue_slide[row:row + tile_size, col: col + tile_size].squeeze()
            wsm_writer.write_tile(tile=tile.astype('uint8'), coordinates=(int(col), int(row)), mask=tile)
    wsm_writer.save()
    parser = MaskAnnotationParser(shape=(512,512), processing_spacing=4.0)
    annotations = parser.parse(mask_output)
    write_asap_annotation(annotations, xml_output)


if __name__ == "__main__":
    main()