from wholeslidedata.annotation.factory import Polygon, Point
import pickle
import numpy as np


class TestAnnotation:
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
