from pathlib import Path
from xmlrpc.client import boolean

import click
from shapely import geometry
from wholeslidedata.accessories.asap.annotationwriter import write_asap_annotation
from wholeslidedata.annotation.structures import Annotation
from wholeslidedata.annotation.utils import cv2_polygonize
from wholeslidedata.image.wholeslideimage import WholeSlideImage
from wholeslidedata.labels import Label


def convert_polygons_to_annotations(polygons, inv_label_map, color_map):
    annotation_structures = []
    index = 0
    for value, polys in polygons.items():
        for polygon in polys:
            p = geometry.Polygon(polygon).buffer(0)
            label = Label(
                name=inv_label_map[value],
                value=value,
                color=color_map[inv_label_map[value]]
            )
            if isinstance(p, geometry.MultiPolygon):
                for q in list(p):
                    annotation_structure = dict(
                        index=index,
                        type="polygon",
                        label=label.todict(),
                        coordinates=q.exterior.coords,
                        holes=[],
                    )
                    annotation_structures.append(annotation_structure)
                    index += 1
            else:
                annotation_structure = dict(
                    index=index,
                    type="polygon",
                    label=label.todict(),
                    coordinates=p.exterior.coords,
                    holes=[],
                )
                annotation_structures.append(annotation_structure)
                index += 1

    annotations = []
    for annotation_structure in annotation_structures:
        if len(annotation_structure["coordinates"]) >= 3:
            try:
                annotation = Annotation.create(**annotation_structure)
            except Exception as e:
                print(annotation_structure["coordinates"])
                raise e
            annotations.append(annotation)
    return annotations


@click.command()
@click.option("--mask_path", type=Path, required=True)
@click.option("--output_folder", type=Path, required=True)
@click.option("--spacing", type=float, required=True)
@click.option("-l", "--label_mapping", multiple=True)
@click.option("-c", "--color_mapping", multiple=True)
@click.option("--dilation_iterations", default=0, type=int, required=False)
@click.option("--erose_iterations", default=0, type=int, required=False)
@click.option("--fill_holes", default=False, type=boolean, required=False)
def main(
    mask_path: Path,
    output_folder: Path,
    spacing: float,
    label_mapping: tuple,
    color_mapping: tuple,
    dilation_iterations: Path,
    erose_iterations: Path,
    fill_holes: float,
):
    output_path = output_folder / (mask_path.stem + ".xml")
    if output_path.exists():
        print(f'xml output path already exist: {output_path}')
        return

    inv_label_map = {
        int(value): key
        for key, value in dict([p.split("=") for p in label_mapping]).items()
    }

    color_map = dict([p.split("=") for p in color_mapping])

    print(f"inv label map: {inv_label_map}")
    if not mask_path.exists():
        raise ValueError(f"mask path {mask_path} does not exists")

    mask = WholeSlideImage(mask_path, backend="asap")
    mask_slide = mask.get_slide(spacing).squeeze()
    scaling = mask.get_downsampling_from_spacing(spacing)
    polygons = cv2_polygonize(
        mask_slide,
        dilation_iterations=dilation_iterations,
        erose_iterations=erose_iterations,
        fill_holes=fill_holes,
        values=list(inv_label_map),
    )
    annotations = convert_polygons_to_annotations(
        polygons=polygons, inv_label_map=inv_label_map, color_map=color_map
    )

    write_asap_annotation(annotations=annotations, output_path=output_path, scaling=1/scaling)


if __name__ == "__main__":
    main()
