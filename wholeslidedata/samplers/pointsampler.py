import abc
from warnings import warn

import numpy as np
import scipy.ndimage as ndi
from shapely import geometry
from wholeslidedata.annotation.structures import Annotation, Point, Polygon
from wholeslidedata.annotation.utils import shift_coordinates
from wholeslidedata.samplers.sampler import Sampler


class PointSampler(Sampler):
    def __init__(self, seed: int):
        self._seed = seed
        self._rng = np.random.RandomState(seed=self._seed)

    def reset(self):
        self._rng = np.random.RandomState(seed=self._seed)

    @abc.abstractmethod
    def sample(self, annotation: Annotation, width: int, height: int, ratio: float):
        pass


@PointSampler.register(('center', ))
class CenterPointSampler(PointSampler):
    """ samples center point"""

    def __init__(self, seed: int, **kwargs):
        super().__init__(seed=seed)

    def sample(self, polygon, width, height, ratio):
        return polygon.center


@PointSampler.register(('centroid', ))
class CentroidPointSampler(PointSampler):
    """ samples center point"""

    def __init__(self, seed: int, **kwargs):
        super().__init__(seed=seed)

    def sample(self, polygon: Polygon, width: int, height: int, ratio: float):
        return polygon.centroid


@PointSampler.register(('top_left', ))
class TopLeftPointSampler(PointSampler):
    """ samples center point"""

    def __init__(self, seed: int, **kwargs):
        super().__init__(seed=seed)

    def sample(self, polygon, width, height, ratio):
        return polygon.bounds[:2]


@PointSampler.register(('random', ))
class RandomPointSampler(PointSampler):
    """ samples points randomly within a polygon with a max limit of 100 otherwise it will return the centroid """

    MAX_ITTERATION = 1000

    def __init__(self, seed: int, strict_point_sampling: bool):
        super().__init__(seed=seed)
        self._strict_point_sampling = strict_point_sampling

    def sample(self, annotation: Annotation, width: int, height: int, ratio: float):
        if isinstance(annotation, Point):
            return annotation.xy[0][0], annotation.xy[1][0]

        for _ in range(RandomPointSampler.MAX_ITTERATION):
            x_min, y_min, x_max, y_max = annotation.bounds
            x_c, y_c = self._rng.uniform(x_min, x_max), self._rng.uniform(y_min, y_max)
            center_shape = (
                geometry.box(
                    x_c - (width * ratio) // 2,
                    y_c - (height * ratio) // 2,
                    x_c + (width * ratio) // 2,
                    y_c + (height * ratio) // 2,
                )
                if self._strict_point_sampling
                else geometry.Point(x_c, y_c)
            )
            if annotation.contains(center_shape):
                return x_c, y_c

        if self._strict_point_sampling:
            warn(
                f"\nCan not find valid point in annotation. \nstrict_point_sampling={self._strict_point_sampling}, \ndata_source={annotation.path}, \nindex={annotation.index} \ndownsampling={ratio}, \nshape=({width}, {height})., return centroid..."
            )
        return np.array(annotation.centroid)

    
@PointSampler.register(('point_density', ))
class PointDensityPointSampler(PointSampler):
    """ samples points based on the density map of the points within a polygon """

    def __init__(
        self,
        dataset,
        seed,
        downsampling_ratio=8,
        gauss_sigma=(10, 10),
        inverse_density_ratio=0.2,
    ):

        super().__init__(seed=seed)
        self._dataset = dataset
        self._downsampling_ratio = downsampling_ratio
        self._sigma = gauss_sigma
        self._inverse_density_ratio = inverse_density_ratio
        self._density_maps = self._load_densities()

    def _load_densities(self):
        density_maps = {}
        for polygon in self._dataset.samples:
            # get size of dense map
            size = (np.array(polygon.size) / self._downsampling_ratio).astype(np.int32)

            # create dense_map laceholder
            dense_map = np.zeros(size[::-1], dtype=np.int32)

            # set labels of all selected annotations
            for annotation in polygon.overlapping_annotations:
                if isinstance(annotation, Point):
                    coordinates = shift_coordinates(
                        annotation.coordinates(),
                        *polygon.center,
                        *size,
                        self._downsampling_ratio,
                    )
                    dense_map[
                        int(coordinates[1]), int(coordinates[0])
                    ] = 1  # annotation.label_value

            d_map = ndi.gaussian_filter(dense_map * 255, self._sigma).astype(np.float64)
            a = d_map - d_map.min()
            b = d_map.max() - d_map.min()
            density_maps[polygon] = np.divide(a, b, out=np.zeros_like(a), where=b != 0)
        return density_maps

    def sample(self, polygon: Polygon, width: int, height: int, ratio: float):
        # TODO check if patch inside polygon
        del width, height, ratio

        density_map = self._density_maps[polygon]

        if self._inverse_density_ratio < np.random.rand():
            choices = (np.random.rand(*density_map.shape) < density_map).astype(int)
        else:
            choices = (np.random.rand(*density_map.shape) < 1 - density_map).astype(int)

        choice_indexes = np.where(choices)

        # if points in annotation
        if choice_indexes[0].shape[0]:
            index = np.random.randint(choice_indexes[0].shape[0])
            x_index, y_index = choice_indexes[1][index], choice_indexes[0][index]

            # offset the x and y coordinates of the sampled patch
            x_c, y_c = (
                x_index * self._downsampling_ratio,
                y_index * self._downsampling_ratio,
            )

            x_min, y_min, _, _ = polygon.bounds
            x_c, y_c = x_c + x_min, y_c + y_min

        # if no point in annotation
        else:
            x_min, y_min, x_max, y_max = polygon.bounds
            x_c, y_c = np.random.uniform(x_min, x_max), np.random.uniform(y_min, y_max)

        return x_c, y_c
