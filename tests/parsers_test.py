from pathlib import Path
from wholeslidedata.annotation.wholeslideannotation import WholeSlideAnnotation
from wholeslidedata.annotation.parser import MaskAnnotationParser
from wholeslidedata.annotation.utils import (
    convert_annotations_to_json,
    write_json_annotations,
)
from wholeslidedata.interoperability.s3.parser import S3AsapAnnotationParser


def test_json_annotations():
    json_path = Path("/tmp/TCGA-21-5784-01Z-00-DX1.json")
    wsa = WholeSlideAnnotation("/tmp/TCGA-21-5784-01Z-00-DX1.xml")
    json_annotations = convert_annotations_to_json(wsa.annotations)
    write_json_annotations(json_path, json_annotations)
    wsa_json = WholeSlideAnnotation(json_path)
    assert len(wsa.annotations) == len(wsa_json.annotations)
    assert wsa.labels.names == wsa_json.labels.names
    json_path.unlink()


def test_mask_annotation_parser():
    annotations = MaskAnnotationParser().parse(
        "/tmp/TCGA-21-5784-01Z-00-DX1_tb_mask.tif"
    )
    assert len(annotations) == 352
    assert set(["tissue"]) == set([annotation.label.name for annotation in annotations])


# def test_s3_annotation_parser():
#     s3_xml_url = 's3://tiger-training/wsirois/wsi-level-annotations/annotations-tissue-bcss-xmls/TCGA-A1-A0SK-01Z-00-DX1.A44D70FA-4D96-43F4-9DD7-A61535786297.xml'
#     wsa = WholeSlideAnnotation(s3_xml_url, parser=S3AsapAnnotationParser)
#     assert len(wsa.labels.names) == 6