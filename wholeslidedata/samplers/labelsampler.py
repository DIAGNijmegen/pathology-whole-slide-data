import copy
import itertools
from typing import Iterator, List, Dict

import numpy as np
from wholeslidedata.samplers.sampler import Sampler


class LabelSampler(Sampler, Iterator):
    def __init__(self, labels: List, seed: int):
        super().__init__(seed=seed)
        self._labels = sorted(labels)
        self._size = len(self._labels)


@LabelSampler.register(("random",))
class RandomLabelSampler(LabelSampler):
    def __init__(self, labels, seed: int = 123):
        super().__init__(labels, seed=seed)

    def __next__(self) -> str:
        return self._labels[self._rng.randint(self._size)]

    def reset(self):
        self.set_seed()


@LabelSampler.register(("ordered",))
class OrderedLabelSampler(LabelSampler):
    def __init__(self, labels: List[str], seed: int = 123):
        super().__init__(labels, seed=seed)
        self._labels_cycle = itertools.cycle(self._labels)
        self.reset()

    def __next__(self):
        return next(self._labels_cycle)

    def reset(self):
        self._labels_cycle = itertools.cycle(self._labels)

    def update(self, batch):
        pass


@LabelSampler.register(("annotation_counted",))
class AnnotationCountedLabelSampler(LabelSampler):
    def __init__(
        self,
        labels: List[str],
        annotations_per_label,
        shuffle=True,
        seed: int = 123,
        random_reset=False,
    ):
        super().__init__(labels, seed=seed)
        self._annotations_per_label = annotations_per_label
        self._shuffle = shuffle
        self._random_reset = random_reset
        self._samples = []
        for label, counts in self._annotations_per_label.items():
            self._samples += [label] * counts

        self._sample_labels = iter(self._samples)
        self.reset()

    def __next__(self):
        try:
            return next(self._sample_labels)
        except StopIteration:
            self.reset()
            return next(self._sample_labels)

    def reset(self):
        self._sample_labels = copy.deepcopy(self._samples)
        if self._shuffle:
            self.set_seed(reseed=self._random_reset)
            self._rng.shuffle(self._sample_labels)
        self._sample_labels = iter(self._sample_labels)

    def update(self, batch):
        pass


@LabelSampler.register(("balanced",))
class BalancedLabelSampler(LabelSampler):
    def __init__(self, labels: List[str], seed: int = 123, random_reset=False):
        super().__init__(labels=labels, seed=seed)
        np.random.shuffle(self._labels)
        self._labels_cycle = iter(self._labels)
        self._random_reset = random_reset
        self.reset()

    def __next__(self):
        try:
            return next(self._labels_cycle)
        except StopIteration:
            self._reset_weak()
            return next(self._labels_cycle)

    def _reset_weak(self):
        labels = self._rng.permutation(self._labels)
        self._labels_cycle = iter(labels)

    def reset(self):
        self.set_seed(reseed=self._random_reset)
        self._reset_weak()

    def update(self, batch):
        pass


@LabelSampler.register(("weighted",))
class WeightedLabelSampler(LabelSampler):
    def __init__(
        self, labels: List[str], weights: List[int], replace=True, seed: int = 123
    ):
        super().__init__(labels=labels, seed=seed)
        self._weights = weights
        self._replace = replace

    def __next__(self):
        return self._rng.choice(self._labels, 1, p=self._weights)[0]

    def update(self, batch):
        pass


@LabelSampler.register(("pixel_counted",))
class PixelCountedLabelSampler(LabelSampler):
    def __init__(self, labels: List[str], seed: int = 123):
        super().__init__(labels=labels, seed=seed)
        self._pixel_count_per_label = {label: 1 for label in self._labels}

    def __next__(self):
        total = sum(self._pixel_count_per_label.values())
        inverse_ratios = {
            label: 1 / (value / total)
            for label, value in self._pixel_count_per_label.items()
        }
        inverse_total = sum(inverse_ratios.values())
        ratios = {
            label: value / inverse_total for label, value in inverse_ratios.items()
        }
        return np.random.choice(list(ratios.keys()), p=list(ratios.values()))

    def update(self, batch):
        _, y_batch = batch
        for label, counts in self._one_hot_encoded_count(y_batch).items():
            self._pixel_count_per_label[label] += counts

    def _one_hot_encoded_count(self, y_batch: np.ndarray) -> Dict[int, int]:
        inv_label_map_indexed = {
            label_index: label for label_index, label in enumerate(self._labels)
        }
        count_per_label = np.sum(
            y_batch, axis=tuple(range(len(np.array(y_batch).shape) - 1))
        )
        return {
            inv_label_map_indexed[label_index]: count
            for label_index, count in enumerate(count_per_label)
        }
