import json
from pathlib import Path
from matplotlib import colors


def write_qupath_annotation(wsa: Path, output_path=None, upsampling_ratio=1.0):
    if output_path is None:
        output_path = wsa.path.parent / (wsa.path.stem + ".json")

    json_content = {}

    for annotation in wsa.annotations:
        label_name = annotation.label.name
        label_color = annotation.label.color if annotation.label.color else "black"
        label_rgb_color = colors.to_rgb(label_color)
        coordinates = annotation.coordinates * upsampling_ratio
        annotation_content = {
            "name": f"Annotation {annotation.index}",
            "color": label_rgb_color,
            "vertices": coordinates.astype(int).tolist(),
        }
        json_content.setdefault(label_name, []).append(annotation_content)

    with open(output_path, "w") as outfile:
        json.dump(json_content, outfile)
