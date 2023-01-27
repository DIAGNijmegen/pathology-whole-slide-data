from wholeslidedata.samplers.annotationsampler import OrderedAnnotationSampler, BalancedAnnotationSampler
from typing import Iterable
import pytest

class TestOrderedAnnotationSampler:
    @pytest.fixture
    def sampler(self):
        counts_per_label = {'label1': 10, 'label2': 20}
        seed = 123
        return OrderedAnnotationSampler(counts_per_label, seed)

    def test_ordered_annotation_sampler_initialization(self, sampler):
        assert sampler._counters == {'label1': 0, 'label2': 0}

    def test_ordered_annotation_sampler_next(self, sampler):
        assert sampler._next('label1') == 0
        assert sampler._next('label1') == 1
        assert sampler._next('label2') == 0
        assert sampler._next('label2') == 1

    def test_ordered_annotation_sampler_reset_label(self, sampler):
        assert sampler._next('label1') == 0
        sampler._reset_label('label1')
        assert sampler._next('label1') == 0

    def test_ordered_annotation_sampler_update(self, sampler):
        data = {'label1': [1, 2, 3], 'label2': [4, 5, 6]}
        sampler.update(data)
        # update method does not change the state of the sampler, so the next sample for 'label1' should still be 0
        assert sampler._next('label1') == 0

    def test_ordered_annotation_sampler_reset(self, sampler):
        assert sampler._next('label1') == 0
        sampler.reset()
        assert sampler._next('label1') == 0



class TestBalancedAnnotationSampler:
    @pytest.fixture
    def sampler(self):
        counts_per_label = {'label1': 10, 'label2': 20}
        seed = 123
        return BalancedAnnotationSampler(counts_per_label, seed)

    def test_balanced_annotation_sampler_initialization(self, sampler):
        assert all(isinstance(counter, Iterable) for counter in sampler._counters.values())

    def test_balanced_annotation_sampler_next(self, sampler):
        # it is not possible to assert on the exact returned values, since they are permutations
        # but we can check that all values are returned at least once before the iterator is reset
        label = 'label1'
        values = set()
        for _ in range(sampler._counts_per_label[label]):
            values.add(sampler._next(label))
        assert len(values) == sampler._counts_per_label[label]

        # after all values are returned, the iterator should be reset and we should start getting the same values again
        for _ in range(sampler._counts_per_label[label]):
            assert sampler._next(label) in values

    def test_balanced_annotation_sampler_update(self, sampler):
        data = {'label1': [1, 2, 3], 'label2': [4, 5, 6]}
        sampler.update(data)
        # update method does not change the state of the sampler, so the next sample for 'label1' should still be a permutation
        label = 'label1'
        values = set()
        for _ in range(sampler._counts_per_label[label]):
            values.add(sampler._next(label))
        assert len(values) == sampler._counts_per_label[label]

    def test_balanced_annotation_sampler_reset(self, sampler):
        label = 'label1'
        values = set()
        for _ in range(sampler._counts_per_label[label]):
            values.add(sampler._next(label))
        assert len(values) == sampler._counts_per_label[label]
        sampler.reset()
        # after resetting, the iterator should be reset and we should start getting the same values again
        for _ in range(sampler._counts_per_label[label]):
            assert sampler._next(label) in values