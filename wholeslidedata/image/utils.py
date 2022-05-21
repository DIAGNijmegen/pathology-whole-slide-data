import cv2

from bisect import bisect_left


def take_closest_level(spacings, spacing):
    pos = bisect_left(spacings, spacing)
    if pos == 0:
        return pos
    if pos == len(spacings):
        return pos - 1
    if spacings[pos] - spacing < spacing - spacings[pos - 1]:
        return pos
    return pos - 1


def create_thumbnail(wsi, output_folder, spacing=8.0):
    slide = wsi.get_slide(spacing)
    output_path = output_folder / (wsi.path.stem + ".png")
    cv2.imwrite(str(output_path), slide)
