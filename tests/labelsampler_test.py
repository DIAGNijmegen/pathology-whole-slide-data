from typing import List
import pytest
from wholeslidedata.samplers.labelsampler import (
    RandomLabelSampler,
    OrderedLabelSampler,
    BalancedLabelSampler,
    AnnotationCountedLabelSampler,
    WeightedLabelSampler,
    PixelCountedLabelSampler,
)
import numpy as np

class TestRandomLabelSampler:
    def test_init(self):
        labels = ["label1", "label2", "label3"]
        sampler = RandomLabelSampler(labels, seed=123)
        assert sampler._labels == labels
        assert sampler._size == 3

    def test_next(self):
        labels = ["label1", "label2", "label3"]
        sampler = RandomLabelSampler(labels, seed=123)
        assert sampler.__next__() in labels
        assert sampler.__next__() in labels
        assert sampler.__next__() in labels

    def test_reset(self):
        labels = ["label1", "label2", "label3"]
        sampler = RandomLabelSampler(labels, seed=123)
        sampler.reset()


class TestOrderedLabelSampler:
    def test_init(self):
        labels = ["label1", "label2", "label3"]
        sampler = OrderedLabelSampler(labels, seed=123)
        assert sampler._labels == labels
        assert sampler._size == 3

    def test_next(self):
        labels = ["label1", "label2", "label3"]
        sampler = OrderedLabelSampler(labels, seed=123)
        assert sampler.__next__() == "label1"
        assert sampler.__next__() == "label2"
        assert sampler.__next__() == "label3"
        assert sampler.__next__() == "label1"
        assert sampler.__next__() == "label2"
        assert sampler.__next__() == "label3"

    def test_reset(self):
        labels = ["label1", "label2", "label3"]
        sampler = OrderedLabelSampler(labels, seed=123)
        assert sampler.__next__() == "label1"
        assert sampler.__next__() == "label2"
        sampler.reset()
        assert sampler.__next__() == "label1"

    def test_update(self):
        labels = ["label1", "label2", "label3"]
        sampler = OrderedLabelSampler(labels, seed=123)
        sampler.update(batch=[])


class TestBalancedLabelSampler:
    def test_init(self):
        labels = ["label1", "label2", "label3"]
        sampler = BalancedLabelSampler(labels, seed=123)
        assert sampler._labels == labels
        assert sampler._size == 3
        assert sampler._random_reset == False

        sampler = BalancedLabelSampler(labels, seed=123, random_reset=True)
        assert sampler._random_reset == True

    def test_next(self):
        labels = ["label1", "label2", "label3"]
        sampler = BalancedLabelSampler(labels, seed=123)
        labels.remove(sampler.__next__())
        labels.remove(sampler.__next__())
        labels.remove(sampler.__next__())
        assert len(labels) == 0
        labels = ["label1", "label2", "label3"]
        labels.remove(sampler.__next__())
        labels.remove(sampler.__next__())
        labels.remove(sampler.__next__())
        assert len(labels) == 0

    def test_reset(self):
        labels = ["label1", "label2", "label3"]
        sampler = BalancedLabelSampler(labels, seed=123)
        label = sampler.__next__()
        sampler.reset()
        assert label == sampler.__next__()

    def test_update(self):
        labels = ["label1", "label2", "label3"]
        sampler = BalancedLabelSampler(labels, seed=123)
        sampler.update(batch=[])


class TestAnnotationCountedLabelSampler:
    @pytest.fixture
    def label_sampler(self):
        labels = ["label1", "label2", "label3"]
        annotations_per_label = {"label1": 3, "label2": 5, "label3": 2}
        return AnnotationCountedLabelSampler(
            labels,
            annotations_per_label,
        )

    def test_init(self, label_sampler):
        # Test that the label sampler is initialized with the correct attributes
        assert label_sampler._labels == ["label1", "label2", "label3"]
        assert label_sampler._annotations_per_label == {
            "label1": 3,
            "label2": 5,
            "label3": 2,
        }
        assert label_sampler._shuffle == True
        assert label_sampler._random_reset == False
        assert label_sampler._samples == [
            "label1",
            "label1",
            "label1",
            "label2",
            "label2",
            "label2",
            "label2",
            "label2",
            "label3",
            "label3",
        ]

    def test_next(self, label_sampler):
        # Test that calling next on the label sampler returns the next label in the list
        labels = list(label_sampler._sample_labels)
        assert next(label_sampler) == labels[0]
        assert next(label_sampler) == labels[1]
        assert next(label_sampler) == labels[2]
        assert next(label_sampler) == labels[3]
        assert next(label_sampler) == labels[4]

    def test_reset(self):
        # Test that resetting the label sampler shuffles the labels and resets the iterator
        labels = ["label1", "label2", "label3"]
        annotations_per_label = {"label1": 3, "label2": 5, "label3": 2}
        label_sampler = AnnotationCountedLabelSampler(
            labels, annotations_per_label, random_reset=True
        )
        label_sampler.reset()
        labels = list(label_sampler._sample_labels)
        label_sampler.reset()
        assert labels != list(label_sampler._sample_labels)

    def test_update(self, label_sampler):
        # Test that the update method does not raise an exception
        label_sampler.update(batch=[])


class TestWeightedLabelSampler:
    @pytest.fixture
    def label_sampler(self):
        labels = {"label1": 0.3, "label2": 0.5, "label3": 0.2}
        return WeightedLabelSampler(labels)

    def test_init(self, label_sampler):
        # Test that the label sampler is initialized with the correct attributes
        assert label_sampler._labels == ["label1", "label2", "label3"]
        assert label_sampler._weights == [0.3, 0.5, 0.2]

    def test_next(self, label_sampler):
        # Test that calling next on the label sampler returns a label according to the weights
        label_counts = {"label1": 0, "label2": 0, "label3": 0}
        counts = 1000
        for _ in range(counts):
            label = next(label_sampler)
            label_counts[label] += 1
        assert label_counts["label1"] / counts > 0.25
        assert label_counts["label1"] / counts < 0.35
        assert label_counts["label2"] / counts > 0.45
        assert label_counts["label2"] / counts < 0.55
        assert label_counts["label3"] / counts > 0.15
        assert label_counts["label3"] / counts < 0.25

    def test_reset(self, label_sampler):
        # Test that resetting the label sampler resets the seed
        label_sampler.reset()
        assert label_sampler._rng.get_state()[1][0] == 123

    def test_update(self, label_sampler):
        # Test that the update method does not raise an exception
        label_sampler.update(batch=[])



class TestPixelCountedLabelSampler:
    @classmethod
    @pytest.fixture
    def sampler(cls):
        labels = ['label1', 'label2', 'label3']
        return PixelCountedLabelSampler(labels=labels)

    def test_init(self, sampler):
        assert sampler._labels == ['label1', 'label2', 'label3']
        assert sampler._pixel_count_per_label == {'label1': 1, 'label2': 1, 'label3': 1}

    def test_next(self, sampler):
        # Test that all labels are returned with equal probability
        # when their pixel counts are equal
        counts = {label: 0 for label in sampler._labels}
        for _ in range(1000):
            label = next(sampler)
            counts[label] += 1
        for count in counts.values():
            assert abs(count - 333) < 50
        
        # Test that the label with the highest pixel count has the lowest probability
        # of being returned
        sampler._pixel_count_per_label['label1'] = 100
        counts = {label: 0 for label in sampler._labels}
        for _ in range(1000):
            label = next(sampler)
            counts[label] += 1
        assert counts['label1'] < 300
        assert counts['label2'] > 300
        assert counts['label3'] > 300



    def test_update(self, sampler):
        # Test that the pixel counts are updated correctly
        y_batch = np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
            [1, 0, 0],
        ])
        sampler.update((None, y_batch))
        assert sampler._pixel_count_per_label == {'label1': 3, 'label2': 2, 'label3': 2}
        y_batch = np.array([
            [0, 0, 1],
            [0, 0, 1],
        ])
        sampler.update((None, y_batch))
        assert sampler._pixel_count_per_label == {'label1': 3, 'label2': 2, 'label3': 4}


    def test_one_hot_encoded_count(self, sampler):
        # Create a test case with 3 labels and a batch of size 2
        y_batch = np.array([[1, 0, 0], [0, 0, 1]])
        # Ensure the count is correct for each label
        expected_count = {'label1': 1, 'label2': 0, 'label3': 1}
        assert sampler._one_hot_encoded_count(y_batch) == expected_count