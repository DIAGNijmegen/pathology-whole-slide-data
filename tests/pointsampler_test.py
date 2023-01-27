
# import pytest
# from wholeslidedata.dataset import DataSet
# from wholeslidedata.mode import WholeSlideMode, create_mode
# from wholeslidedata.labels import Labels, labels_factory
# from wholeslidedata.samplers.pointsampler import PointSampler, CenterPointSampler, CentroidPointSampler
# from sourcelib.associations import Associations, associate_files
# from shapely.geometry import Point
# from wholeslidedata.dataset import WholeSlideSampleReference

# class TestPointSampler:


#     @pytest.fixture
#     def dataset():
#         mode: WholeSlideMode = None
#         associations: Associations = None
#         labels: Labels = None

#         return DataSet(mode=mode, associations=associations, labels=labels)


#     def test_point_sampler_init(self, dataset):
#         # Test that the PointSampler is correctly initialized
#         sampler = PointSampler(seed=123, dataset=dataset)
#         assert sampler._seed == 123
#         assert sampler._dataset == dataset

#     def test_center_point_sampler_init(self, dataset):
#         # Test that the CenterPointSampler is correctly initialized
#         sampler = CenterPointSampler(seed=123, dataset=dataset)
#         assert isinstance(sampler, CenterPointSampler)
#         assert sampler._seed == 123
#         assert sampler._dataset == dataset

#     def test_point_sampler_reset(self, dataset):
#         # Test that the reset method of PointSampler sets a new seed
#         sampler = PointSampler(seed=123, dataset=dataset)
#         sampler.reset()
#         assert sampler._seed != 123

    
#     def test_center_point_sampler_sample(self, dataset):
#         # Test that the sample method of CenterPointSampler returns the correct point
#         center = (1, 2)
#         sample_reference = WholeSlideSampleReference()
#         sampler = CenterPointSampler(seed=123, dataset=dataset)
#         point = sampler.sample(sample_reference)
#         assert point == Point(center)



# class TestCentroidPointSampler:
#     def test_centroid_point_sampler_init(self, dataset):
#         # Test that the CentroidPointSampler is correctly initialized
#         sampler = CentroidPointSampler(seed=123, dataset=dataset)
#         assert isinstance(sampler, CentroidPointSampler)
#         assert sampler._seed == 123
#         assert sampler._dataset == dataset

#     def test_centroid_point_sampler_sample(self, dataset):
#         # Test that the sample method of CentroidPointSampler returns the correct point
#         centroid = (1, 2)
#         sample_reference = WholeSlideSampleReference()
#         sampler = CentroidPointSampler(seed=123, dataset=dataset)
#         point = sampler.sample(sample_reference)
#         assert point == Point(centroid)
        