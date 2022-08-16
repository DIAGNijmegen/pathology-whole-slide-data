import click
from pathlib import Path
from wholeslidedata.accessories.asap.imagewriter import write_mask
from wholeslidedata.image.wholeslideimage import WholeSlideImage
from wholeslidedata.annotation.wholeslideannotation import WholeSlideAnnotation


@click.command()
@click.option("--image_path", type=Path, required=True)
@click.option("--annotation_path", type=Path, required=True)
@click.option("--output_folder", type=Path, required=True)
@click.option("--output_spacing", type=float, required=True)
@click.option("-l", "--label_mapping", multiple=True)
def main(
    image_path: Path,
    annotation_path: Path,
    output_folder: Path,
    output_spacing: float,
    label_mapping: tuple,
):
   
    if len(label_mapping) > 0:
        label_map = {
            key: int(value)
            for key, value in dict([p.split("=") for p in label_mapping]).items()
        }
    else:
        label_map = None
    print(f"label_map: {label_map}")
    if not image_path.exists():
        raise ValueError(f"image input {image_path} does not exists")
    if not annotation_path.exists():
        raise ValueError(f"annotation input {annotation_path} does not exists")

    wsi = WholeSlideImage(image_path, backend="asap")
    wsa = WholeSlideAnnotation(annotation_path, labels=label_map)

    output_folder.mkdir(exist_ok=True, parents=True)
    write_mask(
        wsi=wsi,
        wsa=wsa,
        spacing=output_spacing,
        output_folder=output_folder,
        suffix="_mask.tif",
    )

if __name__ == "__main__":
    main()
