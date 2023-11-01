import json
from typing import List

from wholeslidedata.annotation.labels import Label, Labels
from wholeslidedata.annotation.parser import AnnotationParser


class QuPathAnnotationParser(AnnotationParser):
    @staticmethod
    def get_available_labels(opened_annotation: dict):
        labels = set([annotation["properties"]["classification"]["name"] for annotation in opened_annotation])
        labels = list(zip(labels, list(range(len(labels)))))
        labels = [Label.create(label[0], value=label[1]) for label in labels]
        return Labels.create(labels)

    def _open_annotation(self, path):
        with open(path) as json_file:
            data = json.load(json_file)
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
            ann["type"] = annotation["geometry"]["type"].lower()
            try:
                label_name = annotation["properties"]["classification"]["name"].lower()
            except:
                label_name = None
            if label_name not in labels.names:
                continue
            label = labels.get_label_by_name(label_name)

            for key, value in label.todict().items():
                if key == 'value' or key not in ann["label"] or ann["label"][key] is None:
                    ann["label"][key] = value

            ann["coordinates"] = annotation["geometry"]["coordinates"]

            yield ann