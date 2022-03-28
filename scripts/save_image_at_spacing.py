import argparse
import os
import time
import warnings
from bisect import bisect_left
from pathlib import Path
from shutil import copy

import pyvips

SPACING_MARGIN = 0.3


def take_closest_level(spacings, spacing):
    pos = bisect_left(spacings, spacing)
    if pos == 0:
        return pos
    if pos == len(spacings):
        return pos - 1
    if spacings[pos] - spacing < spacing - spacings[pos - 1]:
        return pos
    return pos - 1


def get_level_from_spacing(spacings, spacing) -> int:
    closest_level = take_closest_level(spacings, spacing)
    spacing_margin = spacing * SPACING_MARGIN
    warning = False
    if abs(spacings[closest_level] - spacing) > spacing_margin:
        warning = True
        warnings.warn(
            f"spacing {spacing} outside margin (0.3%) for {spacings}, returning closest spacing: {spacings[closest_level]}"
        )

    return closest_level, warning


def get_downsamplings(images):
    downsamplings = []
    for idx, image in enumerate(images):
        downsamplings.append(float(image.get(f"openslide.level[{idx}].downsample")))
    return downsamplings


def get_spacings(image_path, images, level_count):
    downsamplings = get_downsamplings(images)

    spacingx = None
    spacingy = None

    try:
        spacingx = float(images[0].get("openslide.mpp-x"))
        spacingy = float(images[0].get("openslide.mpp-y"))
    except:
        try:
            unit = {"cm": 10000, "centimeter": 10000}[
                images[0].get("tiff.ResolutionUnit")
            ]
            xres = float(images[0].get("tiff.XResolution"))
            yres = float(images[0].get("tiff.YResolution"))
            spacingx = unit / xres
            spacingy = unit / yres
        except:
            raise KeyError(image_path, images[0].get_fields())

    return [
        (spacingx * downsamplings[level], spacingy * downsamplings[level])
        for level in range(level_count)
    ]


def write_image_at_spacing(image, spacing, output_path):
    print(f"Writing to {output_path} @ spacing: {spacing}...")
    t1 = time.time()
    image.write_to_file(
        str(output_path),
        pyramid=True,
        tile=True,
        compression="jpeg",
        xres=1000.0 / spacing[0],
        yres=1000.0 / spacing[1],
        bigtiff=True,
    )
    print(f"Writing time: {time.time()-t1}")
    print("Done writing!")


def open_image(image_path, spacing, floor):
    images = []
    images.append(pyvips.Image.openslideload(str(image_path), level=0))
    level_count = int(images[0].get("openslide.level-count"))
    for level in range(1, level_count):
        images.append(pyvips.Image.openslideload(str(image_path), level=level))
    spacings = get_spacings(image_path, images, level_count)
    spacings_x = [spacing[0] for spacing in spacings]
    level, warning = get_level_from_spacing(spacings_x, spacing)
    if floor and spacing < spacings_x[level] and (level - 1) >= 0:
        print("floor==True, lowering level...")
        level -= 1
    return images[level], spacings[level], warning


def _parse_args():
    # create argument parser
    argument_parser = argparse.ArgumentParser(description="Convert Slide")
    argument_parser.add_argument("-i", "--input_data", required=True)
    argument_parser.add_argument("-s", "--spacing", required=True)
    argument_parser.add_argument("-t", "--tmp_folder", required=False)
    argument_parser.add_argument("-o", "--output_folder", required=False)
    argument_parser.add_argument("-e", "--extension", required=False)

    args = vars(argument_parser.parse_args())

    args["input_data"] = Path(args["input_data"])

    args["spacing"] = float(args["spacing"])

    if args["tmp_folder"] is None:
        args["tmp_folder"] = Path("/tmp/")
    else:
        args["tmp_folder"] = Path(args["tmp_folder"])

    if args["output_folder"] is not None:
        args["output_folder"] = Path(args["output_folder"])

    return args


def main():
    args = _parse_args()
    input_data = args["input_data"]
    output_folder = args["output_folder"]
    spacing = args["spacing"]
    tmp_folder = args["tmp_folder"]
    extension = args["extension"]

    if not input_data.exists():
        raise ValueError(f"Input data {input_data} does not exists")

    image_paths = None
    if os.path.isdir(input_data):
        if output_folder is None:
            output_folder = input_data / f"converted_{spacing}"
        if extension is None:
            ValueError(f"Input data {input_data} is a folder, but extension is None")
        image_paths = list(input_data.glob("*." + extension.replace(".", "")))

    if os.path.isfile(input_data):
        if output_folder is None:
            output_folder = (
                input_data.parent / f"converted_{str(spacing).replace('.', '-')}"
            )
        image_paths = [input_data]

    tmp_folder = tmp_folder / "converted"

    output_folder.mkdir(parents=True, exist_ok=True)
    tmp_folder.mkdir(parents=True, exist_ok=True)

    for image_path in image_paths:

        output_path = output_folder / (image_path.stem + ".tif")

        if output_path.exists():
            print(f"Skipping: {output_path} already exists.")
            continue

        print(f"Opening: {image_path}")
        try:
            image, writing_spacing, warning = open_image(
                image_path, spacing, floor=True
            )
        except pyvips.error.Error:
            print(f"ERROR: can not open image: {image_path}")
            continue

        tmp_output_path = tmp_folder / (
            image_path.stem
            + str(writing_spacing[0]).replace(",", "-").replace(".", "-")
            + ".tif"
        )
        write_image_at_spacing(image, writing_spacing, tmp_output_path)

        if warning:
            print(f"Trying to save image closer to spacing: {spacing}...")
            print(f"Opening: {tmp_output_path}")
            image, _writing_spacing, warning = open_image(
                tmp_output_path, spacing, floor=False
            )
            if _writing_spacing != writing_spacing:
                tmp_output_path = tmp_folder / (
                    image_path.stem
                    + str(_writing_spacing[0]).replace(",", "-").replace(".", "-")
                    + ".tif"
                )
                write_image_at_spacing(image, _writing_spacing, tmp_output_path)
            else:
                print(f"Unable to save image closer to spacing: {spacing}")

        print(f"Copying from: {tmp_output_path}...")
        print(f"Copying to: {output_path}...")
        copy(tmp_output_path, output_path)
        print("Done!")


if __name__ == "__main__":
    main()
