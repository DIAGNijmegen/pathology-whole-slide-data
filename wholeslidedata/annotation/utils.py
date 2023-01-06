import json
from typing import List

from wholeslidedata.annotation.labels import Labels
from wholeslidedata.annotation.types import Annotation


def get_labels_in_annotations(annotations):
    return Labels(labels=[annotation.label for annotation in annotations])


def get_counts_in_annotations(annotations, labels=None):
    if labels is None:
        return len(annotations)
    return _counts_per_class(annotations, labels)


def get_pixels_in_annotations(annotations, labels=None):
    if labels is None:
        return int(sum([annotation.area for annotation in annotations]))
    return _pixels_per_class(annotations, labels)


def _counts_per_class(annotations, labels):
    cpc = {label_name: 0 for label_name in labels.names}
    for annotation in annotations:
        cpc[annotation.label.name] += 1
    return cpc


def _pixels_per_class(annotations, labels):
    ppc = {label_name: 0 for label_name in labels.names}
    for annotation in annotations:
        ppc[annotation.label.name] += int(annotation.area)
    return ppc


def convert_annotations_to_json(annotations: List[Annotation]):
    output = []
    for annotation in annotations:
        output.append(annotation.todict())
    return output


def write_json_annotations(output_path, data):
    with open(output_path, "w") as outfile:
        json.dump(data, outfile)
