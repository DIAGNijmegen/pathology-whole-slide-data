from wholeslidedata.annotation.parser import AnnotationParser
from wholeslidedata.labels import Label, Labels

import json 
@AnnotationParser.register(("qupath",))
class QuPathParser(AnnotationParser):
    
    @staticmethod
    def get_available_labels(opened_annotation):
        label_names = []
        for json_annotation in opened_annotation:
            try:
                label_name = json_annotation["properties"]["classification"][
                    "name"
                ].lower()
            except:
                continue
                
            label_names.append(label_name)
        return Labels.create( list(set(label_names)) )
    
    def _open_annotation(self, path):
        with open(path) as json_file:
            json_annotations = json.load(json_file)
        return json_annotations

    
    def _parse(self, path):
        json_annotations = self._open_annotation(path)
        labels = self._get_labels(json_annotations)
        for json_annotation in json_annotations:

            try:
                label_name = json_annotation["properties"]["classification"][
                    "name"
                ].lower()
            except:
                continue
                
            label = self._get_label(label_name, labels)
            if json_annotation["geometry"]["type"].lower() == "polygon":
                annotation_structure = {
                    "type": "polygon",
                    "label": label,
                    "coordinates": json_annotation["geometry"]["coordinates"][0],
                }
                yield annotation_structure

            if json_annotation["geometry"]["type"].lower() == "multipolygon":
                for coords in json_annotation["geometry"]["coordinates"]:
                    annotation_structure = {
                        "type": "polygon",
                        "label": label,
                        "coordinates": coords[0],
                    }
                    yield annotation_structure
                    
    def _get_label(self, label_name, labels):
        label_name = label_name.lower().strip()
        if label_name not in labels.names:
            return None

        label = labels.get_label_by_name(label_name)
        label = label.todict()
        return label