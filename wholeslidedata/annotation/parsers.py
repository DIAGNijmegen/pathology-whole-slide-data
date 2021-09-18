import abc
import json
import xml.etree.ElementTree as ET
from typing import Iterator, List

import numpy as np
from creationism.registration.factory import RegistrantFactory
from shapely import affinity, geometry
from wholeslidedata.annotation.structures import Annotation, AnnotationStructure
from wholeslidedata.labels import Label, Labels

from ..image.wholeslideimage import WholeSlideImage


class InvalidAnnotationParserError(Exception):
    pass


class AnnotationParser(RegistrantFactory):
    def __init__(
        self,
        labels=None,
        renamed_labels=None,
        scaling=1.0,
        sample_annotation_types=("polygon",),
    ):
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

    def read(self, annotation_path, labels=None, renamed_labels=None) -> List[Annotation]:
        if labels is None:
            if self._labels is None:
                labels = self.get_available_labels(annotation_path)
            else:
                labels = self._labels
        else:
            labels = Labels.create(labels)

        if renamed_labels is None:
            renamed_labels = self._renamed_labels
        else:
            renamed_labels = Labels.create(renamed_labels)

        annotations = []
        for annotation_structure in self._get_annotation_structures(
            annotation_path, labels
        ):
            annotation = Annotation.create(
                annotation_structure, labels, renamed_labels, self._scaling
            )

            annotations.append(annotation)
        return annotations

    @property
    def sample_annotation_types(self):
        return self._sample_annotation_types

    def get_available_labels(self, path):
        labels = []
        for annotation_structure in self._get_annotation_structures(path, None):
            labels.append(annotation_structure.label)
        return Labels.create(set(labels))

    @abc.abstractmethod
    def _get_annotation_structures(self, structure) -> Iterator[AnnotationStructure]:
        pass

    @abc.abstractmethod
    def _get_annotation_type(self, structure) -> str:
        pass

    @abc.abstractmethod
    def _get_coordinates(self, structure) -> List:
        pass

    @abc.abstractmethod
    def _get_label_name(self, structure) -> str:
        pass


@AnnotationParser.register(("asap",))
class AsapAnnotationParser(AnnotationParser):

    TYPES = {
        "polygon": "polygon",
        "rectangle": "polygon",
        "dot": "point",
        "spline": "polygon",
        "pointset": "point",
    }

    def get_available_labels(self, path):
        labels = []
        for annotation_structure in self._get_annotation_structures(path, None):
            labels.append(annotation_structure.label)
        return Labels.create(set(labels))

    def _get_annotation_structures(self, path, labels):
        tree = ET.parse(path)
        opened_annotation = tree.getroot()
        annotation_index = 0
        for parent in opened_annotation:
            for child in parent:
                if child.tag == "Annotation":
                    annotation_type = self._get_annotation_type(child)
                    annotation_label = self._get_label_name(child, labels)
                    annotation_coordinates = self._get_coordinates(child)
                    annotation_holes = self._get_holes(child)
                    if not annotation_label or (
                        not isinstance(annotation_label, Label)
                        and isinstance(labels, Labels)
                        and annotation_label not in labels.names
                    ):
                        continue

                    if (
                        isinstance(annotation_label, Label)
                        and isinstance(labels, Labels)
                        and annotation_label.name not in labels.names
                    ):
                        continue

                    if annotation_type == "pointset":
                        for coordinate in annotation_coordinates:
                            annotation_structure = AnnotationStructure(
                                annotation_path=path,
                                index=annotation_index,
                                type=AsapAnnotationParser.TYPES[annotation_type],
                                label=annotation_label,
                                coordinates=[coordinate],
                                holes=annotation_holes,
                            )
                            annotation_index += 1
                            yield annotation_structure
                        continue
                    annotation_structure = AnnotationStructure(
                        annotation_path=path,
                        index=annotation_index,
                        type=AsapAnnotationParser.TYPES[annotation_type],
                        label=annotation_label,
                        coordinates=annotation_coordinates,
                        holes=annotation_holes,
                    )
                    annotation_index += 1
                    yield annotation_structure

    def _get_annotation_type(self, structure):
        annotation_type = structure.attrib.get("Type").lower()
        if annotation_type in AsapAnnotationParser.TYPES:
            return annotation_type
        raise ValueError(f"unsupported annotation type in {structure}")

    def _get_label_name(self, annotation_structure, labels) -> str:
        if (
            isinstance(labels, Labels)
            and self._get_annotation_type(annotation_structure) in labels.names
        ):
            return self._get_annotation_type(annotation_structure).strip()
        return annotation_structure.attrib.get("PartOfGroup").lower().strip()

    def _get_coordinates(self, annotation_structure):
        coordinates = []
        coordinate_structure = annotation_structure[0]
        for coordinate in coordinate_structure:
            coordinates.append(
                (
                    float(coordinate.get("X").replace(",", ".")),
                    float(coordinate.get("Y").replace(",", ".")),
                )
            )
        return coordinates

    def _get_holes(self, annotation_structure):
        return []


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


# @AnnotationParser.register(("mask",))
# class MaskAnnotationParser(AnnotationParser):
#     def __init__(
#         self,
#         shape=(1024, 1024),
#         labels=("tissue",),
#         out_labels=None,
#         scaling=1.0,
#         sample_annotation_types=("Polygon",),
#         backend="asap",
#     ):
#         super().__init__(labels, out_labels, scaling, sample_annotation_types)
#         self._shape = np.array(shape)
#         self._backend = backend

#     def _get_annotation_structures(self, path, labels):
#         mask = WholeSlideImage(path, backend=self._backend)
#         spacing = mask.spacings[0]
#         x_dims, y_dims = mask.shapes[0]

#         x_shift, y_shift = map(int, self._shape // self._scaling)
#         annotation_index = 0
#         for y_pos in range(0, y_dims, y_shift):
#             for x_pos in range(0, x_dims, x_shift):
#                 mask_patch = mask.get_patch(
#                     x_pos,
#                     y_pos,
#                     x_shift,
#                     y_shift,
#                     spacing=spacing,
#                     center=False,
#                 )
#                 labels, counts = self._check_mask(mask_patch)
#                 if labels is not None and counts is not None:
#                     for label, pixels in zip(labels, counts):
#                         if label in self._labels.values:
#                             coordinates = self._get_coordinates(
#                                 x_pos, y_pos, x_shift, y_shift
#                             )
#                             annotation_structure = AnnotationStructure(
#                                 annotation_path=path,
#                                 index=annotation_index,
#                                 type="polygon",
#                                 label=self._labels.get_label_by_value(label).name,
#                                 coordinates=coordinates,
#                                 holes=[],
#                             )
#                             annotation_index += 1
#                             yield annotation_structure

#         mask.close()
#         mask = None
#         del mask

#     def _get_coordinates(self, x_pos, y_pos, x_shift, y_shift) -> List:

#         return [
#             (x_pos, y_pos),
#             (
#                 x_pos,
#                 y_pos + y_shift,
#             ),
#             (
#                 x_pos + x_shift,
#                 y_pos + y_shift,
#             ),
#             (
#                 x_pos + x_shift,
#                 y_pos,
#             ),
#         ]

#     def _check_mask(self, mask_patch):
#         if np.any(mask_patch):
#             return np.unique(mask_patch, return_counts=True)
#         return None, None

#     def _get_annotation_type(self, structure) -> str:
#         return "polygon"

#     def _get_label_name(self, structure) -> str:
#         return "tissue"
