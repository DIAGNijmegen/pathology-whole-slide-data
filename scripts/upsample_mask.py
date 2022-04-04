from pathlib import Path

import click
import numpy as np
from wholeslidedata.accessories.asap.imagewriter import WholeSlideMaskWriter
from wholeslidedata.image.wholeslideimage import WholeSlideImage
from wholeslidedata.iterators import create_patch_iterator
from tqdm import tqdm

def upscale_mask(mask_path, mask_spacing, output_spacing, cpus):

    wsm = WholeSlideImage(mask_path, backend="asap")

    scaling = mask_spacing / output_spacing

    shape = np.array(wsm.shapes[wsm.get_level_from_spacing(2.0)]).astype("uint32")
    spacing = wsm.get_real_spacing(2.0)

    upscaled_shape = shape * scaling
    upscaled_spacing = spacing / scaling
    upscaled_tile_shape = np.array([1024, 1024]).astype("uint32") * scaling

    writer = WholeSlideMaskWriter()

    output_folder: Path = mask_path.parent / f"spacing-{str(output_spacing).replace('.','_')}"
    output_folder.mkdir(parents=True, exist_ok=True)

    output_path = output_folder / mask_path.name.replace(
        ".tif", f"-{str(output_spacing).replace('.','_')}.tif"
    )
    print(f"Upscaling: {mask_path} @ {mask_spacing}")
    print(f"Writing to: {output_path} @ {output_spacing}")

    writer.write(
        path=output_path,
        spacing=upscaled_spacing,
        dimensions=upscaled_shape.astype("int32").tolist(),
        tile_shape=upscaled_tile_shape.astype("int32").tolist(),
    )

    patch_iterator = create_patch_iterator(
        mask_path, mask_spacing, cpus=cpus, scaling=scaling, backend="asap"
    )
    for patch in patch_iterator:
        if np.any(patch[0][0][0]):
            writer.write_tile(
                patch[0][0][0],
                coordinates=[
                    int(patch[1]["x"] * scaling),
                    int(patch[1]["y"] * scaling),
                ],
            )
    patch_iterator.stop()
    print("Done upscaling")
    writer.save()


@click.command()
@click.option("--mask_folder", type=Path, required=True)
@click.option("--suffix", type=str, required=True)
@click.option("--mask_spacing", type=float, required=True)
@click.option("--output_spacing", type=float, required=True)
@click.option("--cpus", type=int, required=True)
def main(mask_folder, suffix, mask_spacing, output_spacing, cpus):
    mask_paths = list(mask_folder.glob("*" + suffix))
    for mask_path in tqdm(mask_paths):
        try:
            upscale_mask(
                mask_path=mask_path,
                mask_spacing=mask_spacing,
                output_spacing=output_spacing,
                cpus=cpus,
            )
        except Exception as e:
            print(f"Error processing {mask_path}")
            print(e)
            print("--------------")


if __name__ == "__main__":
    main()
