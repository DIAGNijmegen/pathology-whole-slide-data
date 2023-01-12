import abc

import numpy as np
from shapely.affinity import affine_transform
from shapely.geometry import Point
from wholeslidedata.samplers.sampler import Sampler


class PointSampler(Sampler):
    @abc.abstractmethod
    def sample(self, annotation):
        pass


class CenterPointSampler(PointSampler):
    """Samples center point"""
    def sample(self, annotation):
        return Point(annotation.center)


class CentroidPointSampler(PointSampler):
    def sample(self, annotation):
        return Point(annotation.centroid)


class TopLeftPointSampler(PointSampler):
    """ Samples top left point"""

    def sample(self, annotation):
        return Point(annotation.bounds[:2])

class RandomPointSampler(PointSampler):
    """Samples uniform point based on triangulation. (based on https://codereview.stackexchange.com/a/204289)
    """

    def __init__(self, buffer=0.0, simplify=2.0, seed=123):
        super().__init__(seed=seed)
        self._buffer = buffer 
        self._simplify = simplify

    def sample(self, annotation):
        buffer = self._buffer
        if isinstance(self._buffer, dict):
            try:
                spacing = annotation.spacing
            except AttributeError:
                raise AttributeError('Using spacing in point sampler but no spacing has been set in the annotation')
            buffer = self._buffer['value'] * (self._buffer['spacing']/spacing)

        record = annotation.triangles(buffer, self._simplify)

        if len(record["transforms"]) == 0:
            return annotation.geometry.representative_point()

        transform_idx = self._rng.choice(
            range(len(record["transforms"])),
            p=np.array(record["areas"]) / sum(record["areas"]),
            size=1,
        )[0]
        transform = record["transforms"][transform_idx]
        x, y = self._rng.random(2)
        if x + y > 1:
            return affine_transform(Point(1 - x, 1 - y), transform)
        return affine_transform(Point(x, y), transform)