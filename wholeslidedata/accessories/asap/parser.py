import xml.etree.ElementTree as ET

from wholeslidedata.annotation.parser import (
    AnnotationParser,
    AnnotationType,
    InvalidAnnotationParserError,
)
from wholeslidedata.labels import Labels

from urllib.parse import urlparse

import boto3
from botocore.handlers import disable_signing

boto_resource = boto3.resource('s3')
boto_resource.meta.client.meta.events.register('choose-signer.s3.*', disable_signing)

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
        # tree = ET.parse(path)
        # opened_annotation = tree.getroot()

        s3_url_parse = urlparse(path, allow_fragments=False)

        s3_bucket_name = s3_url_parse.netloc

        s3_path = s3_url_parse.path.lstrip('/')

        boto_obj = boto_resource.Object(s3_bucket_name, s3_path)

        xmldata = boto_obj.get()["Body"].read().decode('utf-8')

        opened_annotation = ET.fromstring(xmldata)

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
        label = label.todict()
        color = child.attrib.get("Color")
        if 'color' not in label or label['color'] is None:
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
