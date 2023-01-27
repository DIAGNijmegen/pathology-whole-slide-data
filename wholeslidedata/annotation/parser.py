import abc
import json
from enum import Enum
import os
from pathlib import Path
from typing import Any, List, Optional, Union
import warnings

import numpy as np
from wholeslidedata.annotation.types import (
    Annotation,
)
from wholeslidedata.image.wholeslideimage import WholeSlideImage
from wholeslidedata.annotation.labels import Label, Labels
from wholeslidedata.samplers.utils import block
from shapely import geometry


class AnnotationType(Enum):
    POINT = "point"
    POLYGON = "polygon"


class InvalidAnnotationParserError(Exception):
    ...


class AnnotationParser:
    """Base class for parsing annotations. Inherents from RegistrantFactory which allows to register subclasses"""

    def __init__(
        self,
        labels: Optional[Union[Labels, list, tuple, dict]] = None,
        renamed_labels: Optional[Union[Labels, list, tuple, dict]] = None,
        sample_label_names: Union[list, tuple] = (),
        sample_annotation_types: Union[list, tuple] = ("polygon",),
        callbacks=None,
        **kwargs
    ):
        """Init

        Args:
            labels (Optional[Union[Labels, list, tuple, dict]], optional): All labels that are used to parse annotations. Defaults to None.
            renamed_labels (Optional[Union[Labels, list, tuple, dict]], optional): Automatic rename labels based on values. Defaults to None.
            sample_label_names (Union[list, tuple], optional): label names that will be used for sampling. Defaults to ().
            sample_annotation_types (Union[list, tuple], optional): annotation type that will be used for sampling . Defaults to ("polygon",).
        """

        self._labels = labels
        if self._labels is not None:
            self._labels = Labels.create(self._labels)

        self._renamed_labels = renamed_labels
        if self._renamed_labels is not None:
            self._renamed_labels = Labels.create(self._renamed_labels)

        self._sample_annotation_types = [
            annotation_type
            for annotation_type in sample_annotation_types
        ]

        self._sample_label_names = sample_label_names
        self._callbacks = callbacks if callbacks is not None else []
        self._kwargs = kwargs
            

    @classmethod
    def _path_exists(cls, path: str):
        return Path(path).exists()

    @classmethod
    def _empty_file(cls, path: str):
        return os.stat(path).st_size == 0

    @property
    def sample_label_names(self):
        return self._sample_label_names

    @property
    def sample_annotation_types(self):
        return self._sample_annotation_types

    def _rename_label(self, label):
        if self._renamed_labels is None:
            return label
        renamed_label = self._renamed_labels.get_label_by_value(label["value"])
        renamed_label = renamed_label.todict()
        for key, value in label.items():
            if key not in renamed_label or renamed_label[key] is None:
                renamed_label[key] = value
        return renamed_label

    def parse(self, path) -> List[Annotation]:

        if self._empty_file(path):
            warn = f"Loading empty file: {path}"
            warnings.warn(warn)
            return []

        annotations = []
        for index, annotation in enumerate(self._parse(path)):
            annotation["index"] = index
            annotation["coordinates"] = np.array(annotation["coordinates"])
            annotation["label"] = self._rename_label(annotation["label"])
            annotation.update(self._kwargs)
            annotations.append(Annotation.create(**annotation))

        for callback in self._callbacks:
            annotations = callback(annotations)
        return annotations

    def _get_labels(self, opened_annotation):
        if self._labels is None:
            return self.get_available_labels(opened_annotation)
        return self._labels

    @staticmethod
    @abc.abstractmethod
    def get_available_labels(opened_annotation: Any) -> Labels:
        ...

    @abc.abstractmethod
    def _parse(self, path: Union[Path, str]) -> List[dict]:
        ...


class WholeSlideAnnotationParser(AnnotationParser):
    @staticmethod
    def get_available_labels(opened_annotation: dict):
        return Labels.create(
            set(
                [Label.create(annotation["label"]) for annotation in opened_annotation]
            )
        )

    def _open_annotation(self, path):
        with open(path) as json_file:
            return json.load(json_file)

    def _parse(self, path) -> List[dict]:
        if not self._path_exists(path):
            raise FileNotFoundError(path)
            
        data = self._open_annotation(path)
        labels = self._get_labels(data)
        for annotation in data:
            label_name = annotation["label"]["name"]
            if label_name not in labels.names:
                continue
            label = labels.get_label_by_name(label_name)

            for key, value in label.todict().items():
                if key not in annotation["label"] or annotation["label"][key] is None:
                    annotation["label"][key] = value

            yield annotation



class CloudAnnotationParser(WholeSlideAnnotationParser):
    ...