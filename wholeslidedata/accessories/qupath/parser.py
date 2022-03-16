
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
