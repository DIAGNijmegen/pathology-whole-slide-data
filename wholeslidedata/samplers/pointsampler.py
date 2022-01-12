import abc
import random

import numpy as np
from shapely.affinity import affine_transform
from shapely.geometry import Point 
from shapely.ops import triangulate
from shapely.prepared import prep
from wholeslidedata.dataset import DataSet
from wholeslidedata.samplers.sampler import Sampler


class PointSampler(Sampler):
    def __init__(self, seed: int, dataset):
        self._seed = seed
        self._dataset = dataset
        super().__init__(seed=seed)

    def reset(self):
        super().set_seed()

    @abc.abstractmethod
    def sample(self, sample_reference):
        pass


@PointSampler.register(("center",))
class CenterPointSampler(PointSampler):
    """Samples center point"""

    def __init__(self, seed: int, dataset):
        super().__init__(seed=seed, dataset=dataset)

    def sample(
        self,
        sample_reference,
    ):
        return Point(
            self._dataset.get_annotation_from_reference(
                sample_reference=sample_reference
            ).center
        )


@PointSampler.register(("centroid",))
class CentroidPointSampler(PointSampler):
    """Samples centroid point"""

    def __init__(self, seed: int, dataset):
        super().__init__(seed=seed, dataset=dataset)

    def sample(self, sample_reference):
        return Point(
            self._dataset.get_annotation_from_reference(
                sample_reference=sample_reference
            ).centroid
        )


@PointSampler.register(("top_left",))
class TopLeftPointSampler(PointSampler):
    """ Samples top left point"""

    def __init__(self, seed: int, dataset):
        super().__init__(seed=seed, dataset=dataset)

    def sample(self, sample_reference):
        return Point(
            self._dataset.get_annotation_from_reference(
                sample_reference=sample_reference
            ).bounds[:2]
        )


@PointSampler.register(("uniform",))
class UniformPointSampler(PointSampler):
    """Samples uniform point based on triangulation."""

    def __init__(self, seed: int, dataset: DataSet, buffer=0, simplify=2.0):
        super().__init__(seed=seed, dataset=dataset)
        self._sample_map = {}

        for sample_references in dataset.sample_references.values():
            for sample_reference in sample_references:
                annotation = self._dataset.get_annotation_from_reference(
                    sample_reference=sample_reference
                )

                prepped = prep(annotation.buffer(buffer).simplify(simplify))
                triangles = triangulate(annotation.buffer(buffer).simplify(simplify))

                tmp = {
                    tuple(triangle.centroid.coords[0]): triangle
                    for triangle in triangles
                }
                triangle_points = [triangle.centroid for triangle in triangles]
                filtered_points = list(filter(prepped.contains, triangle_points))
                filtered_polys = [tmp[tuple(p.coords[0])] for p in filtered_points]

                areas = []
                transforms = []
                for t in filtered_polys:
                    areas.append(t.area)
                    (x0, y0), (x1, y1), (x2, y2) = t.exterior.coords[:3]
                    transforms.append([x1 - x0, x2 - x0, y1 - y0, y2 - y0, x0, y0])

                record = {
                    "transforms": transforms,
                    "areas": areas,
                    "annotation": annotation,
                }
                self._sample_map[sample_reference] = record

    def sample(self, sample_reference):
        record = self._sample_map[sample_reference]
        if len(record["transforms"]) == 0:
            return record["annotation"].representative_point()

        transform = random.choices(record["transforms"], weights=record["areas"], k=1)[
            0
        ]
        x, y = self._rng.random(2)
        if x + y > 1:
            return affine_transform(Point(1 - x, 1 - y), transform)
        return affine_transform(Point(x, y), transform)


@PointSampler.register(("random",))
class RandomPointSampler(PointSampler):
    """Samples random point based on seek attempts. If no point is found, a representative point is returned"""

    def __init__(self, seed: int, dataset: DataSet, buffer=0, seek_attempts=50):
        super().__init__(seed=seed, dataset=dataset)
        self._sample_map = {}
        for sample_references in dataset.sample_references.values():
            for sample_reference in sample_references:
                annotation = self._dataset.get_annotation_from_reference(
                    sample_reference=sample_reference
                )
                self._sample_map[sample_reference] = (
                    annotation.buffer(buffer).bounds,
                    prep(annotation.buffer(buffer)),
                    seek_attempts,
                    annotation.representative_point(),
                )

    def sample(self, sample_reference):

        bounds, prepped_annotation, size, representative_point = self._sample_map[
            sample_reference
        ]
        if not bounds:
            return representative_point

        x_min, y_min, x_max, y_max = bounds
        x_c, y_c = self._rng.uniform(x_min, x_max, size=size), self._rng.uniform(
            y_min, y_max, size=size
        )
        points = [Point(x, y) for x, y in zip(x_c, y_c)]
        fpoints = list(filter(prepped_annotation.contains, points))
        if len(fpoints) == 0:
            return representative_point
        return fpoints[0]
