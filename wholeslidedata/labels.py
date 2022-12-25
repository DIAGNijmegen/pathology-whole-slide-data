from dataclasses import dataclass
from typing import Any, List, Union
from warnings import warn
from functools import singledispatch


class CreateLabelsError(Exception):
    pass


class LabelValueError(Exception):
    pass


@dataclass(frozen=True)
class NegativeLabelValueWarning(Warning):
    ...


class Label:
    def __init__(self, name: str, value: int):
        self._name = str(name).lower()
        self._value = value

        if not isinstance(value, int):
            raise LabelValueError(f"label value {value} should be an integer")

        if value < 0:
            warn(NegativeLabelValueWarning())

    def __eq__(self, other):
        if isinstance(other, Label):
            return self.name == other.name and self.value == other.value
        return False

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    def todict(self):
        return dict(name=self.name, value=self.value)

    def __str__(self):
        return f"Label({', '.join([f'{key}={value}' for key, value in self.todict().items()])})"


class Labels:
    def __init__(self, labels: List[Label]):
        self._labels = labels
        self._label_by_name = {label.name: label for label in self._labels}
        self._label_by_value = {label.value: label for label in self._labels}

    def __getitem__(self, idx):
        return self._labels[idx]

    def __setitem__(self, idx, value):
        self._labels[idx] = label_factory(value, idx=idx)

    def __len__(self):
        return len(self._labels)

    def __iter__(self):
        return iter(self._labels)

    @property
    def map(self):
        return {label.name: label.value for label in self._labels}

    @property
    def name_map(self):
        return self._label_by_name

    @property
    def value_map(self):
        return self._label_by_value

    @property
    def names(self):
        return list(self._label_by_name.keys())

    @property
    def values(self):
        return list(self._label_by_value.keys())

    def get_label_by_value(self, value):
        try:
            return self._label_by_value[value]
        except KeyError:
            raise KeyError(f"no label value {value}")

    def get_label_by_name(self, name):
        try:
            return self._label_by_name[name]
        except KeyError:
            raise KeyError(f"no label with name {name}")


def label_factory(label: Any, **kwargs):
    return _label_factory(label, **kwargs)


@singledispatch
def _label_factory(label: Any):
    raise ValueError("Unsupported label type", type(label))


@_label_factory.register
def _label_from_label(label: Label, **kwargs):
    return label


@_label_factory.register
def _label_from_dict(label: dict, **kwargs):
    return Label(**label)


@_label_factory.register
def _label_from_str(label: str, value: int):
    return Label(name=label, value=value)


def labels_factory(labels: Any):
    return _labels_factory(labels)


@singledispatch
def _labels_factory(labels: Any):
    return Labels([Label(key, value) for key, value in labels.items()])


@_labels_factory.register
def _labels_from_labels(labels: Labels):
    return labels


@_labels_factory.register
def _labels_from_dict(labels: dict):
    return Labels([Label(key, value) for key, value in labels.items()])


@_labels_factory.register(set)
@_labels_factory.register(tuple)
@_labels_factory.register(list)
def _labels_from_collection(labels: Union[set, tuple, list]):
    return Labels(
        [label_factory(label, value=idx + 1) for idx, label in enumerate(labels)]
    )