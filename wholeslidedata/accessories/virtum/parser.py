


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


