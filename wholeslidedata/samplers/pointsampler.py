import abc
import random
from warnings import warn

import numpy as np
import scipy.ndimage as ndi
from shapely import geometry
from shapely.affinity import affine_transform
from shapely.ops import triangulate
from shapely.prepared import prep
from wholeslidedata.annotation.structures import Annotation, Point, Polygon
from wholeslidedata.annotation.utils import shift_coordinates
from wholeslidedata.dataset import DataSet
from wholeslidedata.samplers.sampler import Sampler
from shapely.geometry import Point as ShapelyPoint


class PointSampler(Sampler):
    def __init__(self, seed: int, dataset):
        self._seed = seed
        self._dataset = dataset
        self._rng = np.random.RandomState(seed=self._seed)
        random.seed(self._seed)

    def reset(self):
        self._rng = np.random.RandomState(seed=self._seed)
        random.seed(self._seed)

    @abc.abstractmethod
    def sample(self, sample_reference):
        pass


@PointSampler.register(("center",))
class CenterPointSampler(PointSampler):
    """ samples center point"""

    def __init__(self, seed: int, dataset):
        super().__init__(seed=seed, dataset=dataset)

    def sample(
        self,
        sample_reference,
    ):
        return ShapelyPoint(self._dataset.get_annotation_from_reference(
            sample_reference=sample_reference
        ).center)


@PointSampler.register(("centroid",))
class CentroidPointSampler(PointSampler):
    """ samples center point"""

    def __init__(self, seed: int, dataset):
        super().__init__(seed=seed, dataset=dataset)

    def sample(self, sample_reference):
        return self._dataset.get_annotation_from_reference(
            sample_reference=sample_reference
        ).centroid


@PointSampler.register(("top_left",))
class TopLeftPointSampler(PointSampler):
    """ samples center point"""

    def __init__(self, seed: int, dataset):
        super().__init__(seed=seed, dataset=dataset)

    def sample(self, sample_reference):
        return self._dataset.get_annotation_from_reference(
            sample_reference=sample_reference
        ).bounds[:2]


@PointSampler.register(("uniform",))
class UniformPointSampler(PointSampler):
    def __init__(self, seed: int, dataset: DataSet, simplify=2.0):
        super().__init__(seed=seed, dataset=dataset)
        print('initializing uniform point sampler')
        self._sample_map = {}
        for sample_references in dataset.sample_references.values():
            for sample_reference in sample_references:
                annotation = self._dataset.get_annotation_from_reference(
                    sample_reference=sample_reference
                )
                prepped = prep(annotation.buffer(0).simplify(simplify))
                triangles = triangulate(annotation.buffer(0).simplify(simplify))

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

                record = {"transforms": transforms, "areas": areas}
                self._sample_map[sample_reference] = record
        print('DONE (initializing fast uniform point sampler)')
        
    def sample(self, sample_reference):
        record = self._sample_map[sample_reference]
        transform = random.choices(record["transforms"], weights=record["areas"], k=1)[0]
        x, y = self._rng.random(2)
        if x + y > 1:
            return affine_transform(ShapelyPoint(1 - x, 1 - y), transform)
        return affine_transform(ShapelyPoint(x, y), transform)


# strict reduce polygon size into inner reverse dilate

@PointSampler.register(('random', ))
class RandomPointSampler(PointSampler):
    """ samples points randomly within a polygon with a max limit of 10 otherwise it will return the centroid """
    def __init__(self, seed: int, dataset, sample_size=100):
        super().__init__(seed=seed, dataset=dataset)
        self._sample_map = {}
        for sample_references in dataset.sample_references.values():
            for sample_reference in sample_references:
                annotation = self._dataset.get_annotation_from_reference(
                    sample_reference=sample_reference
                )
                size = max(1, int(annotation.area/(100*100)))
                self._sample_map[sample_reference]= (annotation.bounds, prep(annotation), size, annotation.representative_point())

    def sample(self, sample_reference):
        bounds, prepped_annotation, size, representative_point = self._sample_map[sample_reference]
        x_min, y_min, x_max, y_max = bounds

        x_c, y_c = np.random.uniform(x_min, x_max, size=size), np.random.uniform(y_min, y_max, size=size)
        points = [ShapelyPoint(x, y) for x, y in zip(x_c, y_c)]
        fpoints = list(filter(prepped_annotation.contains, points))
        if len(fpoints) == 0:
            return representative_point
        return fpoints[0]

# @PointSampler.register(('point_density', ))
# class PointDensityPointSampler(PointSampler):
#     """ samples points based on the density map of the points within a polygon """

#     def __init__(
#         self,
#         dataset,
#         seed,
#         downsampling_ratio=8,
#         gauss_sigma=(10, 10),
#         inverse_density_ratio=0.2,
#     ):

#         super().__init__(seed=seed)
#         self._dataset = dataset
#         self._downsampling_ratio = downsampling_ratio
#         self._sigma = gauss_sigma
#         self._inverse_density_ratio = inverse_density_ratio
#         self._density_maps = self._load_densities()

#     def _load_densities(self):
#         density_maps = {}
#         for polygon in self._dataset.samples:
#             # get size of dense map
#             size = (np.array(polygon.size) / self._downsampling_ratio).astype(np.int32)

#             # create dense_map laceholder
#             dense_map = np.zeros(size[::-1], dtype=np.int32)

#             # set labels of all selected annotations
#             for annotation in polygon.overlapping_annotations:
#                 if isinstance(annotation, Point):
#                     coordinates = shift_coordinates(
#                         annotation.coordinates(),
#                         *polygon.center,
#                         *size,
#                         self._downsampling_ratio,
#                     )
#                     dense_map[
#                         int(coordinates[1]), int(coordinates[0])
#                     ] = 1  # annotation.label_value

#             d_map = ndi.gaussian_filter(dense_map * 255, self._sigma).astype(np.float64)
#             a = d_map - d_map.min()
#             b = d_map.max() - d_map.min()
#             density_maps[polygon] = np.divide(a, b, out=np.zeros_like(a), where=b != 0)
#         return density_maps

#     def sample(self, polygon: Polygon, width: int, height: int, ratio: float):
#         # TODO check if patch inside polygon
#         del width, height, ratio

#         density_map = self._density_maps[polygon]

#         if self._inverse_density_ratio < np.random.rand():
#             choices = (np.random.rand(*density_map.shape) < density_map).astype(int)
#         else:
#             choices = (np.random.rand(*density_map.shape) < 1 - density_map).astype(int)

#         choice_indexes = np.where(choices)

#         # if points in annotation
#         if choice_indexes[0].shape[0]:
#             index = np.random.randint(choice_indexes[0].shape[0])
#             x_index, y_index = choice_indexes[1][index], choice_indexes[0][index]

#             # offset the x and y coordinates of the sampled patch
#             x_c, y_c = (
#                 x_index * self._downsampling_ratio,
#                 y_index * self._downsampling_ratio,
#             )

#             x_min, y_min, _, _ = polygon.bounds
#             x_c, y_c = x_c + x_min, y_c + y_min

#         # if no point in annotation
#         else:
#             x_min, y_min, x_max, y_max = polygon.bounds
#             x_c, y_c = np.random.uniform(x_min, x_max), np.random.uniform(y_min, y_max)

#         return x_c, y_c
