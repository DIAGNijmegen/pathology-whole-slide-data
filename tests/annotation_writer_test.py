

from pathlib import Path
from wholeslidedata.annotation.labels import Label
from wholeslidedata.annotation.types import Annotation
from wholeslidedata.interoperability.asap.annotationwriter import write_asap_annotation, write_point_set
from wholeslidedata.annotation.wsa import WholeSlideAnnotation
import random

def test_write_asap_annotations():
    file1 = Path("/tmp/TCGA-21-5784-01Z-00-DX1.xml")
    file2 = Path("/tmp/TCGA-21-5784-01Z-00-DX1_new.xml")
    wsi1 = WholeSlideAnnotation(file1)
    write_asap_annotation(wsi1.annotations + [Annotation.create(index=11, label=Label.create(label="point", value=4), coordinates=[1,1])], output_path=file2)
    assert file2.exists()
    wsi2 = WholeSlideAnnotation(file2)
    assert len(wsi1.annotations) == len(wsi2.annotations)-1
    assert set(wsi1.labels.names+ ['point']) == set(wsi2.labels.names)
    file2.unlink()


def test_write_point_set():
    points = []
    output_path = Path('/tmp/pointset.xml')
    for _ in range(1000):
        points.append(Annotation.create(index=11, label=Label.create(label="point", value=1), coordinates=[random.randint(1, 50000),random.randint(1, 50000)]))
    write_point_set(points, output_path)
    wsa = WholeSlideAnnotation(output_path)
    assert len(wsa.annotations) == 1000
    assert wsa.labels.names == ['point']
    assert wsa.labels.values == [1]
    output_path.unlink()