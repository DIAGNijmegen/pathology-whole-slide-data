import os
import shutil
import tempfile
import unittest
from pathlib import Path

from tests.testdata import download_wsa, download_wsi
from wholeslidedata.annotation.structures import Polygon, Point
import pickle
import numpy as np

from wholeslidedata.annotation.wholeslideannotation import WholeSlideAnnotation
from wholeslidedata.annotation.wholeslideannotationwriter import convert_annotations


class TestAnnotation(unittest.TestCase):
    def test_polygon_properties(self):
        polygon = Polygon(
            index=0,
            annotation_path="",
            label="square",
            coordinates=[[0, 0], [0, 2], [2, 2], [2, 0], [0, 0]],
        )
        polygon2 = Polygon(
            index=1,
            annotation_path="",
            label="square",
            coordinates=[[0, 0], [0, 4], [4, 4], [4, 0], [0, 0]],
        )
        assert polygon.area == 4
        assert polygon.centroid == (1, 1)
        assert polygon.center == (1, 1)
        assert polygon.size == (2, 2)
        assert polygon.bounds == [0, 0, 2, 2]
        assert polygon.annotation_path == ""
        assert polygon.label == "square"
        assert polygon.iou(polygon2) == 0.25
        assert np.all(
            polygon.coordinates == np.array([[0, 0], [0, 2], [2, 2], [2, 0], [0, 0]])
        )
        assert polygon2.contains(polygon)
        assert not polygon.contains(polygon2)

    def test_polygon_hole(self):
        polygon = Polygon(
            index=0,
            annotation_path="",
            label="square",
            coordinates=[[0, 0], [0, 2], [2, 2], [2, 0], [0, 0]],
        )
        polygon2 = Polygon(
            index=1,
            annotation_path="",
            label="square",
            coordinates=[[0, 0], [0, 4], [4, 4], [4, 0], [0, 0]],
            holes=[[[0, 0], [0, 2], [2, 2], [2, 0], [0, 0]]],
        )
        assert polygon.iou(polygon2) == 0
        assert not polygon2.contains(polygon)

    def test__pickle(self):
        pickle.dumps(
            Polygon(
                index=0,
                annotation_path="",
                label="square",
                coordinates=[[0, 0], [0, 2], [2, 2], [2, 0], [0, 0]],
            )
        )
        pickle.dumps(
            Point(index=3, annotation_path="", label="square", coordinates=[[2, 2]])
        )

    def test_polygon_overlapping_annotations(self):
        polygon = Polygon(
            index=0,
            annotation_path="",
            label="square",
            coordinates=[[0, 0], [0, 3], [3, 3], [3, 0], [0, 0]],
        )
        polygon2 = Polygon(
            index=1,
            annotation_path="",
            label="square",
            coordinates=[[1, 1], [1, 4], [4, 4], [4, 1], [1, 1]],
        )
        assert not polygon2.contains(polygon)
        assert not polygon.contains(polygon2)

        point = Point(index=3, annotation_path="", label="square", coordinates=[[2, 2]])
        assert polygon.contains(point)
        polygon.add_overlapping_annotations([polygon2])
        assert not polygon.contains(point)

    def test_parse_colour_from_annotation(self):
        xml_string = """<?xml version="1.0"?>
        <ASAP_Annotations>
            <Annotations>
                <Annotation Name="test_annotation" Type="Rectangle" PartOfGroup="test" Color="#F4FA58">
                    <Coordinates>
                        <Coordinate Order="0" X="70316.8047" Y="94614.7422" />
                        <Coordinate Order="1" X="72576.6484" Y="94614.7422" />
                        <Coordinate Order="2" X="72576.6484" Y="96517.4375" />
                        <Coordinate Order="3" X="70316.8047" Y="96517.4375" />
                    </Coordinates>
                </Annotation>
                </Annotations>
            <AnnotationGroups>
                <Group Name="test" PartOfGroup="None" Color="#ff0000"> <Attributes /> </Group>
            </AnnotationGroups>
        </ASAP_Annotations>
        """
        dir_path = tempfile.mkdtemp()
        test_annotation_path = os.path.join(dir_path, "test_annotation.xml")
        with open(test_annotation_path, "w") as xml:
            xml.write(xml_string)

        wsa = WholeSlideAnnotation(test_annotation_path)
        self.assertIsNotNone(wsa)
        self.assertEqual(wsa.annotations[0].label.color, "#F4FA58")
        shutil.rmtree(dir_path)

    def test_parse_colour_from_annotations_xml(self):
        dir_path = tempfile.mkdtemp()
        annotation_path = download_wsa(dir_path)
        wsa = WholeSlideAnnotation(annotation_path)
        self.assertIsNotNone(wsa)
        self.assertRegex(wsa.annotations[0].label.color, r"^#([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$")
        shutil.rmtree(dir_path)

    def test_convert_annotations_colors(self):
        dir_path = tempfile.mkdtemp()
        annotation_path = download_wsa(dir_path)
        wsa = WholeSlideAnnotation(annotation_path)
        color = wsa.annotations[0].label.color
        self.assertIsNotNone(wsa)
        convert_annotations(Path(annotation_path).parent, Path(annotation_path).parent, scaling=1.0)
        wsa_changed = WholeSlideAnnotation(annotation_path)
        self.assertTrue(color, wsa_changed.annotations[0].label.color)
