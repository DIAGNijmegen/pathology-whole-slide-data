import json
from pathlib import Path

import numpy as np
from matplotlib import colors


def write_qupath_annotation(wsa: Path, output_path=None, upsampling_ratio=1.0):
    # the root of the xml file
    if output_path is None:
        output_path = wsa.path.parent / (wsa.path.stem + ".json")

    labels = set()
    json_content = {}

    for annotation in wsa.annotations:
        label_name = annotation.label.name
        label_color = annotation.label.color if annotation.label.color else "black"
        label_rgb_color = colors.to_rgb(label_color)
        index = annotation.index
        polygon = annotation.buffer(1)
        coordinates = polygon.exterior.coords
        coordinates = np.array(coordinates) * upsampling_ratio
        coordinates = coordinates.astype(int).tolist()
        annotation_content = {
            "name": f"Annotation {index}",
            "color": label_rgb_color,
            "vertices": list(coordinates),
        }
        json_content.setdefault(label_name, []).append(annotation_content)

    with open(output_path, "w") as outfile:
        json.dump(json_content, outfile)
