import abc
import json
from enum import Enum
import os
from pathlib import Path
from typing import Any, List, Optional, Union
import warnings

import numpy as np
from creationism.registration.factory import RegistrantFactory
from wholeslidedata.annotation.hooks import AnnotationHook
from wholeslidedata.annotation.structures import Annotation
from wholeslidedata.image.wholeslideimage import WholeSlideImage
from wholeslidedata.labels import Label, Labels
from wholeslidedata.samplers.utils import block_shaped
from shapely import geometry

SCHEMA = {
    "type": "object",
    "required": ["type", "label", "coordinates"],
    "additionalProperties": False,
    "properties": {
        "type": {"enum": ["polygon", "point"]},
        "coordinates": {
            "type": "array",
            "items": {
                "type": "array",
                "contains": {"type": "number"},
                "minContains": 2,
                "maxContains": 2,
            },
        },
        "label": {
            "type": "object",
            "required": ["name", "value"],
            "properties": {
                "name": {"type": "string"},
                "value": {"type": "integer", "minimum": 0},
                "color": {"type": "string"},
                "weight": {"type": "number"},
                "confidence": {"type": "number"},
                "overlay_index": {"type": "integer"},
            },
        },
        "index": {"type": "integer", "minimum": 0},
    },
}


class AnnotationType(Enum):
    POINT = "point"
    POLYGON = "polygon"


class InvalidAnnotationParserError(Exception):
    ...



class AnnotationParser(RegistrantFactory):
    """Base class for parsing annotations. Inherents from RegistrantFactory which allows to register subclasses"""

    def __init__(
        self,
        labels: Optional[Union[Labels, list, tuple, dict]] = None,
        renamed_labels: Optional[Union[Labels, list, tuple, dict]] = None,
        sample_label_names: Union[list, tuple] = (),
        sample_annotation_types: Union[list, tuple] = ("polygon",),
        hooks = (),
        **kwargs,
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
            Annotation.get_registrant(annotation_type)
            for annotation_type in sample_annotation_types
        ]

        self._sample_label_names = sample_label_names
        
        self._hooks = list(hooks)
        for key, value in kwargs.items():
            self._hooks.append(AnnotationHook.create(key, False, value))


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

        if not self._path_exists(path):
            raise FileNotFoundError(path)

        if self._empty_file(path):
            warn = f"Loading empty file: {path}"
            warnings.warn(warn)
            return []

        annotations = []
        for index, annotation in enumerate(self._parse(path)):
            annotation["index"] = index
            annotation["coordinates"] = np.array(annotation["coordinates"]) 
            annotation["label"] = self._rename_label(annotation["label"])
            annotations.append(Annotation.create(**annotation))

        for hook in self._hooks:
            annotations = hook(annotations)
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


@AnnotationParser.register(("wsa",))
class WholeSlideAnnotationParser(AnnotationParser):
    @staticmethod
    def get_available_labels(opened_annotation: dict):
        return Labels.create(
            set([Label.create(annotation["label"]) for annotation in opened_annotation])
        )

    def _parse(self, path) -> List[dict]:
        with open(path) as json_file:
            data = json.load(json_file)
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


@AnnotationParser.register(("mask",))
class MaskAnnotationParser(AnnotationParser):
    def __init__(
        self,
        labels=("tissue",),
        processing_spacing=4.0,
        output_spacing=0.5,
        shape=(1024, 1024),
        backend="asap",
        full_coverage=False,
    ):
        super().__init__(labels=labels)
        self._processing_spacing = processing_spacing
        self._output_spacing = output_spacing
        self._shape = np.array(shape)
        self._backend = backend
        self._np_check_tissue = np.all if full_coverage else np.any

    def get_available_labels(opened_annotation: Any) -> Labels:
        return Labels.create({'tissue': 1})

    def _parse(self, path):
        mask = WholeSlideImage(path, backend=self._backend)

        size = self._shape[0]
        ratio = self._processing_spacing / self._output_spacing

        np_mask = mask.get_slide(self._processing_spacing).squeeze()
        shape = np.array(np_mask.shape)

        new_shape = shape + size // ratio - shape % (size // ratio)
        new_mask = np.zeros(new_shape.astype("int"), dtype="uint8")
        new_mask[: shape[0], : shape[1]] = np_mask

        for annotation in self._get_annotations(new_mask, size, ratio):
            yield annotation

        mask.close()
        mask = None
        del mask

    def _get_annotations(self, new_mask, size, ratio):
        region_index = -1
        blocks = block_shaped(new_mask, int(size // ratio), int(size // ratio))
        for y in range(new_mask.shape[0] // (int(size // ratio))):
            for x in range(new_mask.shape[1] // int((size // ratio))):
                region_index += 1
                if not self._np_check_tissue(blocks[region_index]):
                    continue

                box = self._get_coordinates(x * size, y * size, size, size)
                yield {
                    "type": AnnotationType.POLYGON.value,
                    "coordinates": np.array(box),
                    "label": {"name": "tissue", "value": 1},
                }


    def _get_coordinates(self, x_pos, y_pos, x_shift, y_shift) -> List:
        box = geometry.box(x_pos, y_pos, x_pos+x_shift, y_pos+y_shift)
        return np.array(box.exterior.xy).T.tolist()

    def _check_mask(self, mask_patch):
        if np.any(mask_patch):
            return np.unique(mask_patch, return_counts=True)
        return None, None

class CloudAnnotationParser(WholeSlideAnnotationParser):
    ...