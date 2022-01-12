from typing import Callable, Dict, Iterator
import abc
import numpy as np
from wholeslidedata.samplers.sampler import Sampler


class AnnotationSampler(Sampler, Iterator):
    def __init__(self, counts_per_label: Dict, seed: int):
        super().__init__(seed=seed)
        self._counts_per_label = dict(sorted(counts_per_label.items()))

    def __next__(self) -> Callable:
        return self._next

    @abc.abstractmethod
    def _next(self, label: str) -> int:
        pass

    @abc.abstractmethod
    def update(self, data):
        pass


@AnnotationSampler.register(("ordered",))
class OrderedAnnotationSampler(AnnotationSampler):
    def __init__(self, counts_per_label, seed):
        super().__init__(counts_per_label=counts_per_label, seed=seed)
        self._counters = {label: 0 for label in self._counts_per_label.keys()}
        self.reset()

    def _next(self, label):
        annotation_index = self._counters[label]
        self._counters[label] += 1
        if self._counters[label] == self._counts_per_label[label]:
            self._reset_label(label)
        return annotation_index

    def _reset_label(self, label):
        self._counters[label] = 0

    def update(self, data):
        pass

    def reset(self):
        self.set_seed()
        for label in self._counts_per_label.keys():
            self._reset_label(label)


@AnnotationSampler.register(("balanced",))
class BalancedAnnotationSampler(AnnotationSampler):
    def __init__(self, counts_per_label, seed, random_reset=False):
        super().__init__(counts_per_label, seed=seed)
        self._counters = {
            label: self._random_index_iterator(label)
            for label in self._counts_per_label
        }
        self._random_reset = random_reset

    def _next(self, label):
        try:
            return next(self._counters[label])
        except StopIteration:
            self._reset_label(label)
            return next(self._counters[label])

    def _random_index_iterator(self, label):
        return iter(self._rng.permutation(range(self._counts_per_label[label])))

    def update(self, data):
        pass

    def _reset_label(self, label):
        self._counters[label] = self._random_index_iterator(label)

    def reset(self):
        self.set_seed(reseed=self._random_reset)
        for label in self._counts_per_label.keys():
            self._reset_label(label)


@AnnotationSampler.register(("weighted",))
class WeightedAnnotationSampler(AnnotationSampler):
    def __init__(
        self,
        counts_per_label,
        seed,
        samples,
        standard_weight=0.2,
        normalize_value=255.0,
    ):
        super().__init__(counts_per_label, seed=seed)
        self._Annotationes = {
            label: list(range(counts))
            for label, counts in self._counts_per_label.items()
        }
        self._Annotation_weights = {}
        for label_name, annotations in samples.items():
            label_weights = []
            for annotation in annotations:
                if annotation.label.weight is not None:
                    label_weights.append(annotation.label.weight / normalize_value)
                else:
                    label_weights.append(standard_weight)
            label_weights = np.array(label_weights)
            self._Annotation_weights[label_name] = label_weights / sum(label_weights)

    def _next(self, label):
        return np.random.choice(
            self._Annotationes[label], 1, p=self._Annotation_weights[label]
        )[0]

    def update(self, data):
        pass

    def _reset_label(self, label):
        pass

    def reset(self):
        super().set_seed()


@AnnotationSampler.register(("area",))
class AreaAnnotationSampler(AnnotationSampler):
    def __init__(self, counts_per_label, seed, samples, weight=1.0):
        super().__init__(counts_per_label, seed=seed)

        self._weight = weight
        self._area_Annotation_map = {label: {} for label in counts_per_label}
        self._total_area = {label: 0 for label in counts_per_label}

        # calculate here to save time in __next__
        self._area_Annotationes = {
            label: np.zeros(counts) for label, counts in counts_per_label.items()
        }

        for label, values in samples.items():
            for annotation_Annotation, annotation in enumerate(values):
                self._area_Annotation_map[label][
                    self._total_area[label]
                ] = annotation_Annotation
                self._area_Annotationes[label][
                    annotation_Annotation
                ] = self._total_area[label]
                self._total_area[label] += annotation.area ** self._weight

        self.reset()

    def _next(self, label):
        rint = np.random.randint(self._total_area[label])
        area_Annotation = np.where((rint >= self._area_Annotationes[label]))[0][-1]
        return self._area_Annotation_map[label][
            self._area_Annotationes[label][area_Annotation]
        ]

    def update(self, data):
        pass

    def _reset_label(self, label):
        pass

    def reset(self):
        super().set_seed()
