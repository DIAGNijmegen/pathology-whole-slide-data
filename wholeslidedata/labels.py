from dataclasses import dataclass
from typing import Any, List
from warnings import warn

from creationism.registration.factory import RegistrantFactory


class CreateLabelsError(Exception):
    pass


class LabelValueError(Exception):
    pass


@dataclass(frozen=True)
class NegativeLabelValueWarning(Warning):
    ...


class Label(RegistrantFactory):
    @classmethod
    def create(cls, label: Any, *args, **kwargs):
        return super().create(registrant_name=type(label), label=label, *args, **kwargs)

    def __init__(
        self,
        name: str,
        value: int,
        overlay_index: int = 1,
        weight: float = None,
        color: str = "black",
        **kwargs,
    ):

        self._name = str(name).lower()
        self._value = value
        self._weight = weight
        self._overlay_index = overlay_index
        self._color = color

        if not isinstance(value, int):
            raise LabelValueError(f"label value {value} should be an integer")

        if value < 0:
            warn(NegativeLabelValueWarning())

        if weight is not None and not isinstance(weight, (int, float)):
            raise LabelValueError(f"label weight {value} should be a number")

        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def name(self):
        return self._name

    def set_name(self, name):
        self._name = str(name).lower()

    def set_color(self, color):
        self._color = color

    @property
    def value(self):
        return self._value

    @property
    def weight(self):
        return self._weight

    @property
    def overlay_index(self):
        return self._overlay_index

    @property
    def color(self):
        return self._color


@Label.register_func((Label,))
def label_from_label(label: Label, *args, **kwargs):
    return label


@Label.register_func((dict,))
def label_from_dict(label: dict, *args, **kwargs):
    return Label(**label)


@Label.register_func((str,))
def label_from_str(label: str, idx: int, *args, **kwargs):
    return Label(name=label, value=idx)


class Labels(RegistrantFactory):
    @classmethod
    def create(cls, labels):
        return super().create(registrant_name=type(labels), labels=labels)

    def __init__(self, labels: List[Label]):
        self._labels = labels
        self._label_by_name = {label.name: label for label in self._labels}
        self._label_by_value = {label.value: label for label in self._labels}

    def __getitem__(self, idx):
        return self._labels[idx]

    def __setitem__(self, idx, value):
        self._labels[idx] = Label.create(value, idx=idx)

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


@Labels.register_func((Labels,))
def labels_from_dict(labels: Labels):
    return labels


@Labels.register_func((dict,))
def labels_from_dict(labels: dict):
    return Labels([Label(key, value) for key, value in labels.items()])


@Labels.register_func((tuple, set, list))
def labels_from_collection(labels):
    return Labels(
        [Label.create(label=label, idx=idx + 1) for idx, label in enumerate(labels)]
    )
