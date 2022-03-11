import abc
import xml.etree.ElementTree as ET
from typing import List, Optional, Union

import numpy as np
from creationism.registration.factory import RegistrantFactory
from enum import Enum
from wholeslidedata.annotation.structures import Annotation
from wholeslidedata.image.wholeslideimage import WholeSlideImage
from wholeslidedata.labels import Label, Labels
from wholeslidedata.samplers.utils import block_shaped
import json

SCHEMA = {
    "type": "object",
    "required": ["type", "label", "coordinates"],
    "additionalProperties": False,
    "properties": {
        "type": {"enum": ["polygon", "point"]},
        "coordinates": {
            "type": "array",
            "items": {
                "type": "array",
                "contains": {"type": "number"},
                "minContains": 2,
                "maxContains": 2,
            },
        },
        "label": {
            "type": "object",
            "required": ["name", "value"],
            "properties": {
                "name": {"type": "string"},
                "value": {"type": "integer", "minimum": 0},
                "color": {"type": "string"},
                "weight": {"type": "number"},
                "confidence": {"type": "number"},
                "overlay_index": {"type": "integer"},
            },
        },
        "index": {"type": "integer", "minimum": 0},
    },
}


class AnnotationType(Enum):
    POINT = "point"
    POLYGON = "polygon"


class InvalidAnnotationParserError(Exception):
    pass


class AnnotationParser(RegistrantFactory):
    """Base class for parsing annotations. Inherents from RegistrantFactory which allows to register subclasses"""

    def __init__(
        self,
        labels: Optional[Union[Labels, list, tuple, dict]] = None,
        renamed_labels: Optional[Union[Labels, list, tuple, dict]] = None,
        scaling: float = 1.0,
        sample_label_names: Union[list, tuple] = (),
        sample_annotation_types: Union[list, tuple] = ("polygon",),
    ):
        """Init

        Args:
            labels (Optional[Union[Labels, list, tuple, dict]], optional): All labels that are used to parse annotations. Defaults to None.
            renamed_labels (Optional[Union[Labels, list, tuple, dict]], optional): Automatic rename labels based on values. Defaults to None.
            scaling (float, optional): scaling factor for annotations. Defaults to 1.0.
            sample_label_names (Union[list, tuple], optional): label names that will be used for sampling. Defaults to ().
            sample_annotation_types (Union[list, tuple], optional): annotation type that will be used for sampling . Defaults to ("polygon",).
        """

        self._labels = labels
        if self._labels is not None:
            self._labels = Labels.create(self._labels)

        self._renamed_labels = renamed_labels
        if self._renamed_labels is not None:
            self._renamed_labels = Labels.create(self._renamed_labels)

        self._scaling = scaling
        self._sample_annotation_types = [
            Annotation.get_registrant(annotation_type)
            for annotation_type in sample_annotation_types
        ]

        self._sample_label_names = sample_label_names

    @property
    def sample_label_names(self):
        return self._sample_label_names

    @property
    def sample_annotation_types(self):
        return self._sample_annotation_types

    @property
    def scaling(self):
        return self._scaling

    def _rename_label(self, label):
        if self._renamed_labels is None:
            return label
        renamed_label = self._renamed_labels.get_label_by_value(label["value"])
        renamed_label = renamed_label.properties
        for key, value in label.items():
            if key not in renamed_label or renamed_label[key] is None:
                renamed_label[key] = value
        return renamed_label

    def parse(self, path) -> List[Annotation]:
        annotations = []
        for annotation in self._parse(path):
            annotation["coordinates"] = np.array(annotation["coordinates"]) * self._scaling
            annotation["label"] = self._rename_label(annotation["label"])
            annotations.append(Annotation.create(**annotation))
        return annotations

    @staticmethod
    def get_available_labels(opened_annotation):
        return Labels.create(set([Label.create(annotation["label"]) for annotation in opened_annotation]))

    def _get_labels(self, path):
        if self._labels is None:
            return self.get_available_labels(path)
        return self._labels

    def _parse(self, path) -> List[dict]:
        with open(path) as json_file:
            data = json.load(json_file)

        labels = self._get_labels(data)
        for annotation in data:
            label_name = annotation["label"]["name"]
            if label_name not in labels.names:
                continue
            label = labels.get_label_by_name(label_name)
            annotation['label'].update(label.properties)
            yield annotation


@AnnotationParser.register(("asap",))
class AsapAnnotationParser(AnnotationParser):

    TYPES = {
        "polygon": AnnotationType.POLYGON,
        "rectangle": AnnotationType.POLYGON,
        "dot": AnnotationType.POINT,
        "spline": AnnotationType.POLYGON,
        "pointset": AnnotationType.POINT,
    }

    @staticmethod
    def get_available_labels(opened_annotation):
        labels = []
        for parent in opened_annotation:
            for child in parent:
                if child.tag == "Annotation":
                    labels.append(child.attrib.get("PartOfGroup").lower().strip())
        return Labels.create(set(labels))

    def _parse(self, path):
        tree = ET.parse(path)
        opened_annotation = tree.getroot()
        labels = self._get_labels(opened_annotation)
        for parent in opened_annotation:
            for child in parent:

                if child.tag != "Annotation":
                    continue

                type = self._get_annotation_type(child)

                label = self._get_label(child, labels, type)
                if label is None:
                    continue

                for coordinates in self._yield_coordinates(child, type):
                    yield {
                        "type": type.value,
                        "coordinates": coordinates,
                        "label": label,
                    }

    def _get_annotation_type(self, child):
        annotation_type = child.attrib.get("Type").lower()
        if annotation_type in AsapAnnotationParser.TYPES:
            return AsapAnnotationParser.TYPES[annotation_type]
        raise ValueError(f"unsupported annotation type in {child}")

    def _get_label(self, child, labels: Labels, type):
        name = self._get_label_name(child, labels, type)
        if name not in labels.names:
            return None

        label = labels.get_label_by_name(name)
        label = label.properties
        color = child.attrib.get("Color")
        if color:
            label["color"] = color

        return label

    def _get_label_name(self, child, labels, type) -> str:
        if type in labels.names:
            return type
        return child.attrib.get("PartOfGroup").lower().strip()

    def _yield_coordinates(self, child, type):
        coordinates = []
        coordinate_structure = child[0]
        coordinates = self._get_coordinates(coordinate_structure)
        if type is AnnotationType.POLYGON:
            if len(coordinates) < 3:
                raise InvalidAnnotationParserError(f"Polygon contains < 3 coordinates")
            yield coordinates
        elif type is AnnotationType.POINT and len(coordinates) > 1:
            for coordinate in coordinates:
                yield coordinate
        else:
            yield coordinates[0]

    def _get_coordinates(self, coordinate_structure):
        return [
            [
                float(coordinate.get("X").replace(",", ".")),
                float(coordinate.get("Y").replace(",", ".")),
            ]
            for coordinate in coordinate_structure
        ]


# @AnnotationParser.register(("hnasap",))
# class HnAsapAnnotationParser(AsapAnnotationParser):
#     def _get_label_name(self, annotation_structure, labels) -> str:
#         if (
#             isinstance(labels, Labels)
#             and self._get_annotation_type(annotation_structure) in labels.names
#         ):
#             return self._get_annotation_type(annotation_structure).strip()

#         label_name = annotation_structure.attrib.get("PartOfGroup").lower().strip()
#         label_and_weight = label_name.split("-weight=")
#         if len(label_and_weight) == 1:
#             return label_and_weight[0]

#         label_name, weight = label_and_weight
#         return Label(label_name, labels.map[label_name], weight=float(weight))


# @AnnotationParser.register(("virtum",))
# class VirtumAnnotationParser(AnnotationParser):
#     def get_available_labels(self, path):
#         labels = []
#         for annotation_structure in self._get_annotation_structures(path, None):
#             labels.append(annotation_structure.label)
#         return Labels.create(set(labels))

#     def _get_annotation_structures(self, path, labels):
#         tree = ET.parse(path)
#         vsannotations = []
#         name_to_group = {}
#         for parent in tree.getroot():
#             for child in parent:
#                 if child.tag == "Annotation":
#                     vsannotations.append(child)
#                 if child.tag == "Group":
#                     group = child
#                     name = group.attrib.get("Name")
#                     if name and "tissue" not in name and "holes" not in name:
#                         partofgroup = group.attrib.get("PartOfGroup")
#                         if partofgroup != "None":
#                             name_to_group[group.attrib.get("Name")] = group.attrib.get(
#                                 "PartOfGroup"
#                             )

#         opened_annotation = []
#         for idx, annotation in enumerate(vsannotations):
#             label_reference = "_".join(
#                 annotation.attrib.get("PartOfGroup").split("_")[:-1]
#             )
#             hole = annotation.attrib.get("PartOfGroup").split("_")[-1] == "holes"
#             if hole:
#                 label = "hole"
#             elif label_reference:
#                 label = name_to_group[label_reference].lower()
#             else:
#                 label = annotation.attrib.get("PartOfGroup").lower()

#             coordinates = []
#             for coords in annotation:
#                 coordinates = [
#                     (
#                         float(coord.get("X").replace(",", ".")),
#                         float(coord.get("Y").replace(",", ".")),
#                     )
#                     for coord in coords
#                 ]
#             annotation_type = self._get_annotation_type(annotation)

#             if annotation_type != "dot" and label == "hole":
#                 opened_annotation[-1]["holes"].append(coordinates)
#             else:
#                 opened_annotation.append(
#                     {
#                         "type": annotation_type,
#                         "label": label,
#                         "coordinates": coordinates,
#                         "holes": [],
#                     }
#                 )

#         for annotation_index, annotation in enumerate(opened_annotation):
#             annotation_label = annotation["label"]

#             if not annotation_label or (
#                 not isinstance(annotation_label, Label)
#                 and isinstance(labels, Labels)
#                 and annotation_label not in labels.names
#             ):
#                 continue
#             annotation_structure = AnnotationStructure(
#                 annotation_path=path,
#                 index=annotation_index,
#                 type=AsapAnnotationParser.TYPES[annotation["type"]],
#                 label=annotation["label"],
#                 coordinates=annotation["coordinates"],
#                 holes=annotation["holes"],
#             )

#             yield annotation_structure

#     def _get_annotation_type(self, structure):
#         annotation_type = structure.attrib.get("Type").lower()
#         if annotation_type in AsapAnnotationParser.TYPES:
#             return annotation_type
#         raise ValueError(f"unsupported annotation type in {structure}")

#     def _get_label_name(self, annotation_structure, labels) -> str:
#         if (
#             isinstance(labels, Labels)
#             and self._get_annotation_type(annotation_structure) in labels.names
#         ):
#             return self._get_annotation_type(annotation_structure).strip()
#         return annotation_structure.attrib.get("PartOfGroup").lower().strip()

#     def _get_coordinates(self, annotation_structure) -> List:
#         return annotation_structure["coordinates"]

#     def _get_holes(self, annotation_structure):
#         return annotation_structure["holes"]


# @AnnotationParser.register(("qupath",))
# class QuPathParser(AnnotationParser):
#     def _get_annotation_structures(self, path, labels) -> Iterator:
#         with open(path) as json_file:
#             json_annotations = json.load(json_file)

#         annotation_index = 0
#         for json_annotation in json_annotations:

#             try:
#                 label_name = json_annotation["properties"]["classification"][
#                     "name"
#                 ].lower()
#             except:
#                 label_name = None

#             if not label_name or (
#                 not isinstance(label_name, Label)
#                 and isinstance(labels, Labels)
#                 and label_name not in labels.names
#             ):
#                 continue

#             if json_annotation["geometry"]["type"].lower() == "polygon":
#                 annotation_structure = AnnotationStructure(
#                     annotation_path=path,
#                     index=annotation_index,
#                     type="polygon",
#                     label=label_name,
#                     coordinates=json_annotation["geometry"]["coordinates"][0],
#                     holes=[],
#                 )
#                 annotation_index += 1
#                 yield annotation_structure

#             if json_annotation["geometry"]["type"].lower() == "multipolygon":
#                 for coords in json_annotation["geometry"]["coordinates"]:
#                     annotation_structure = AnnotationStructure(
#                         annotation_path=path,
#                         index=annotation_index,
#                         type="polygon",
#                         label=label_name,
#                         coordinates=coords[0],
#                         holes=[],
#                     )
#                     annotation_index += 1
#                     yield annotation_structure

#     def _get_annotation_type(self, annotation_structure) -> str:
#         return "polygon"

#     def _get_coordinates(self, annotation_structure) -> List:
#         return annotation_structure["coordinates"]

#     def _get_label_name(self, annotation_structure) -> str:
#         return annotation_structure["label_name"]

#     def _get_holes(self, annotation_structure):
#         return []


# @AnnotationParser.register(("htk",))
# class HTKAnnotationParser(AnnotationParser):
#     def _get_annotation_structures(self, path, labels) -> Iterator:
#         with open(path) as json_file:
#             json_annotations = json.load(json_file)

#         annotation_index = 0
#         for json_annotation in json_annotations:
#             for annotation_structure in json_annotation["annotation"]["elements"]:
#                 annotation_coordinates = self._get_coordinates(annotation_structure)
#                 annotation_type = self._get_annotation_type(annotation_structure)
#                 annotation_label = self._get_label_name(annotation_structure)
#                 annotation_holes = self._get_holes(annotation_structure)

#                 if not annotation_label or (
#                     not isinstance(annotation_label, Label)
#                     and isinstance(labels, Labels)
#                     and annotation_label not in labels.names
#                 ):
#                     continue

#                 annotation_structure = AnnotationStructure(
#                     annotation_path=path,
#                     index=annotation_index,
#                     type=AsapAnnotationParser.TYPES[annotation_type],
#                     label=annotation_label,
#                     coordinates=annotation_coordinates,
#                     holes=annotation_holes,
#                 )
#                 annotation_index += 1
#                 yield annotation_structure

#     def _get_annotation_type(self, annotation_structure) -> str:
#         return "polygon"

#     def _get_coordinates(self, annotation_structure) -> List:
#         # parse rectangle
#         if annotation_structure["type"] == "rectangle":
#             center = annotation_structure["center"]
#             width = annotation_structure["width"]
#             height = annotation_structure["height"]

#             x1, y1 = (
#                 center[0] - width // 2,
#                 center[1] - height // 2,
#             )
#             x2, y2 = (
#                 x1 + annotation_structure["width"],
#                 y1 + annotation_structure["height"],
#             )
#             coordinates = [[x1, y1], [x1, y2], [x2, y2], [x2, y1]]
#             if (
#                 "rotation" in annotation_structure
#                 and annotation_structure["rotation"] != 0
#             ):
#                 rotation = annotation_structure["rotation"]
#                 p = geometry.Polygon(coordinates)

#                 rotated = affinity.rotate(p, rotation, use_radians=True)
#                 coordinates = list(rotated.exterior.coords)[:-1]  # first=last point
#             return coordinates

#         # parse polygon
#         points = annotation_structure["points"]
#         coordinates = [point[:2] for point in points]
#         return coordinates

#     def _get_label_name(self, annotation_structure) -> str:
#         if "label" not in annotation_structure:
#             return None
#         return annotation_structure["label"]["value"]

#     def _get_holes(self, annotation_structure):
#         return []


@AnnotationParser.register(("mask",))
class MaskAnnotationParser(AnnotationParser):
    def __init__(
        self,
        labels=("tissue",),
        processing_spacing=4.0,
        output_spacing=0.5,
        shape=(1024, 1024),
        backend="asap",
    ):
        super().__init__(labels=labels)
        self._processing_spacing = processing_spacing
        self._output_spacing = output_spacing
        self._shape = np.array(shape)
        self._backend = backend

    def _parse(self, path):
        mask = WholeSlideImage(path, backend=self._backend)

        size = self._shape[0]
        ratio = self._processing_spacing / self._output_spacing

        np_mask = mask.get_slide(self._processing_spacing).squeeze()
        shape = np.array(np_mask.shape)

        new_shape = shape + size // ratio - shape % (size // ratio)
        new_mask = np.zeros(new_shape.astype("int"), dtype="uint8")
        new_mask[: shape[0], : shape[1]] = np_mask

        blocks = block_shaped(new_mask, int(size // ratio), int(size // ratio))

        region_index = -1
        for y in range(new_mask.shape[0] // (int(size // ratio))):
            for x in range(new_mask.shape[1] // int((size // ratio))):
                region_index += 1
                if not np.any(blocks[region_index]):
                    continue

                box = self._get_coordinates(x * size, y * size, size, size)
                yield {
                    "type": AnnotationType.POLYGON.value,
                    "coordinates": np.array(box),
                    "label": {"name": "tissue", "value": 1},
                }

        mask.close()
        mask = None
        del mask

    def _get_coordinates(self, x_pos, y_pos, x_shift, y_shift) -> List:

        return [
            [x_pos, y_pos],
            [
                x_pos,
                y_pos + y_shift,
            ],
            [
                x_pos + x_shift,
                y_pos + y_shift,
            ],
            [
                x_pos + x_shift,
                y_pos,
            ],
            [x_pos, y_pos],
        ]

    def _check_mask(self, mask_patch):
        if np.any(mask_patch):
            return np.unique(mask_patch, return_counts=True)
        return None, None
