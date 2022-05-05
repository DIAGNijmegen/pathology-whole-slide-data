import xml.etree.ElementTree as ET
from wholeslidedata.annotation.parser import AnnotationParser
from wholeslidedata.labels import Labels


@AnnotationParser.register(("virtum-asap",))
class VirtumAsapAnnotationParser(AnnotationParser):
    @staticmethod
    def get_available_labels(opened_annotation):
        name_to_group = {}
        for parent in opened_annotation.getroot():
            for child in parent:
                if child.tag == "Group":
                    group = child
                    name = group.attrib.get("Name")
                    if name and "tissue" not in name and "holes" not in name:
                        partofgroup = group.attrib.get("PartOfGroup")
                        if partofgroup != "None":
                            name_to_group[group.attrib.get("Name")] = group.attrib.get(
                                "PartOfGroup"
                            )
        return Labels.create(set(list(name_to_group.values())))
                             
    def _parse(self, path):
        tree = ET.parse(path)
        vsannotations = []
        name_to_group = {}
        for parent in tree.getroot():
            for child in parent:
                if child.tag == "Annotation":
                    vsannotations.append(child)
                if child.tag == "Group":
                    group = child
                    name = group.attrib.get("Name")
                    if name and "tissue" not in name and "holes" not in name:
                        partofgroup = group.attrib.get("PartOfGroup")
                        if partofgroup != "None":
                            name_to_group[group.attrib.get("Name")] = group.attrib.get(
                                "PartOfGroup"
                            )
        labels = self._get_labels(tree)
        opened_annotation = []
        for annotation in vsannotations:
            label_reference = "_".join(
                annotation.attrib.get("PartOfGroup").split("_")[:-1]
            )
            hole = annotation.attrib.get("PartOfGroup").split("_")[-1] == "holes"
            if hole:
                label ='hole'
            elif label_reference:
                label = name_to_group[label_reference].lower()
            else:
                label = annotation.attrib.get("PartOfGroup").lower()

            coordinates = []
            for coords in annotation:
                coordinates = [
                    (
                        float(coord.get("X").replace(",", ".")),
                        float(coord.get("Y").replace(",", ".")),
                    )
                    for coord in coords
                ]
            annotation_type = annotation.attrib.get("Type").lower()

            if annotation_type == "dot":
                raise ValueError('points/dots not supported')
        
            if label == "hole":
                opened_annotation[-1]["holes"].append(coordinates)
            else:
                label = labels.get_label_by_name(label)
                label = label.todict()
                opened_annotation.append(
                    {
                        "type": 'polygon',
                        "label": label,
                        "coordinates": coordinates,
                        "holes": [],
                    }
                )

        for annotation in opened_annotation:
            yield annotation
 