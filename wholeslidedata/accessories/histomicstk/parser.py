
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