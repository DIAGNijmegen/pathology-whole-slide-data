import argparse
import re
from pathlib import Path
from pprint import pprint

def _scale_line(line: str, scale_factor: float):
    for i in ('X="(.*?)"{1}', 'Y="(.*?)"{1}'):
        ireg = re.search(i, line)
        if ireg is not None:
            coord_setting = ireg.group()
            coordinate = re.search('"(.*)"', coord_setting).group(1).strip()
            scaled_coordinate = str(float(coordinate.replace(',', '.')) * scale_factor)
            coord_setting_scaled = coord_setting.replace(coordinate, scaled_coordinate)
            line = line.replace(coord_setting, coord_setting_scaled)
    return line


def scale(path: Path, output_folder: Path, scale_factor: float):
    print(f'Processing: {path}')
    with open(path) as infile:
        if output_folder is None:
            output_folder = path.parent

        output_path = output_folder / (path.name.replace(".xml", f"_rescaled.xml"))
        
        print(f'Creating: {output_path}')
        with open(output_path, "w") as outfile:
            for line in infile:
                line = _scale_line(line, scale_factor=scale_factor)
                outfile.write(line)


def main(path: Path, scale_factor: float, output_folder: Path = None):
    if not path.exists():
        raise ValueError(f"Path: {path} does not exists")

    if path.is_dir():
        for p in list(path.glob("*.xml")):
            scale(path=p, output_folder=output_folder, scale_factor=scale_factor)
    elif path.suffix == ".xml":
        scale(path=path, output_folder=output_folder, scale_factor=scale_factor)
    else:
        raise ValueError(f"Invalid input: {path}")


def _parse_args():
    # create argument parser
    argument_parser = argparse.ArgumentParser(description="scale asap annotations")
    argument_parser.add_argument("-i", "--input", required=True)
    argument_parser.add_argument("-s", "--scale_factor", required=True)
    argument_parser.add_argument("-o", "--output_folder", required=False)

    args = vars(argument_parser.parse_args())

    args["input"] = Path(args["input"])
    args["scale_factor"] = float(args["scale_factor"])

    if args["output_folder"] is not None:
        args["output_folder"] = Path(args["output_folder"])

    return args


if __name__ == "__main__":
    args = _parse_args()
    print('---Args---')
    pprint(args)
    main(
        path=args["input"],
        output_folder=args["output_folder"],
        scale_factor=args["scale_factor"],
    )
    print('---Completed---')
