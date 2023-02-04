from pathlib import Path

import click
from wholeslidedata import WholeSlideAnnotation
from wholeslidedata.annotation.utils import (
    convert_annotations_to_json,
    write_json_annotations,
)


@click.command()
@click.option("--input_folder", type=Path, required=True)
@click.option("--output_folder", type=Path, required=True)
def main(input_folder: Path, output_folder: Path):
    output_folder.mkdir(parents=True, exist_ok=True)
    for xml in list(input_folder.glob("*xml")):
        output_path = output_folder / (xml.stem + ".json")
        json_data = convert_annotations_to_json(WholeSlideAnnotation(xml).annotations)
        write_json_annotations(output_path=output_path, data=json_data)


if __name__ == "__main__":
    main()
