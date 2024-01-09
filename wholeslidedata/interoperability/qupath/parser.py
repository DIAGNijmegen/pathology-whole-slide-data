import json
from typing import List

from wholeslidedata.annotation.labels import Label, Labels
from wholeslidedata.annotation.parser import AnnotationParser


class QuPathAnnotationParser(AnnotationParser):
    @staticmethod
    def get_available_labels(opened_annotation: dict):
        labels = set(
            [
        annotation.get("properties", {}).get("classification", {}).get("name")
        for annotation in opened_annotation
        if annotation.get("properties", {}).get("classification") and annotation.get("properties", {}).get("classification", {}).get("name")
            ]
        )
        labels = list(zip(labels, list(range(len(labels)))))
        labels = [Label.create(label[0], value=label[1]) for label in labels]
        return Labels.create(labels)

    def _open_annotation(self, path):
        with open(path) as json_file:
            data = json.load(json_file)
            if isinstance(data, dict) and "features" in data:
                data = data['features']
            if type(data) is not list:
                data = [data]
            return data

    def _parse(self, path) -> List[dict]:
        if not self._path_exists(path):
            raise FileNotFoundError(path)

        data = self._open_annotation(path)
        labels = self._get_labels(data)
        for annotation in data:
            ann = dict()
            ann["label"] = dict()
            geom_type = annotation["geometry"]["type"].lower()
            try:
                label_name = annotation["properties"]["classification"]["name"].lower()
            except:
                label_name = None
            if label_name not in labels.names:
                continue
            label = labels.get_label_by_name(label_name)

            for key, value in label.todict().items():
                if (
                    key == "value"
                    or key not in ann["label"]
                    or ann["label"][key] is None
                ):
                    ann["label"][key] = value

            _coords = annotation["geometry"]["coordinates"]

            if geom_type == "polygon":
                if len(_coords) == 1:
                    ann["coordinates"] = _coords[0]
                else:
                    ann["coordinates"] = {
                        "coordinates": _coords[0],
                        "holes": _coords[1:],
                    }
                yield ann
            elif geom_type == "multipolygon":
                for coordinates in _coords:
                    if len(coordinates) == 1:
                        yield {
                            "label": ann["label"],
                            "coordinates": coordinates[0],
                        }
                    else:
                        yield {
                            "label": ann["label"],
                            "coordinates": {
                                "coordinates": coordinates[0],
                                "holes": coordinates[1:],
                            },
                        }
            else:
                raise ValueError(
                    f"Annotation type {geom_type} is not supported yet."
                    f"Only polygon and multipolygon are supported."
                )
