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
from wholeslidedata.annotation.selector import sort_by_label_value
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
        sorters=tuple(),
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

        self._sample_annotation_types = sample_annotation_types

        self._sample_label_names = sample_label_names
        self._callbacks = callbacks if callbacks is not None else []
        self._sorters = sorters
        self._kwargs = kwargs
            

    @classmethod
    def _path_exists(cls, path: str):
        return Path(path).exists()

    @classmethod
    def _empty_file(cls, path: str):
        return os.stat(path).st_size == 0

    @property
    def sorters(self):
        return self._sorters
    
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

    def parse(self, path, spacing=None) -> List[Annotation]:

        if self._empty_file(path):
            warn = f"Loading empty file: {path}"
            warnings.warn(warn)
            return []

        annotations = []
        sample_annotations = []

        for index, annotation in enumerate(self._parse(path)):
            annotation["index"] = index
            annotation["label"] = self._rename_label(annotation["label"])
            if spacing is not None:
                annotation["spacing"] = spacing
            annotation.update(self._kwargs)
            annotations.append(Annotation.create(**annotation))
            
            if len(self._callbacks)>0:
                sample_annotations.append(Annotation.create(**annotation))
        
        if len(self._callbacks)>0:
            for callback in self._callbacks:
                sample_annotations = callback(sample_annotations)
        else:
            sample_annotations = annotations

        return annotations, sample_annotations

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
                if key == 'value' or key not in annotation["label"] or annotation["label"][key] is None:
                    annotation["label"][key] = value

            yield annotation


class MaskAnnotationParser(AnnotationParser):
    def __init__(
        self,
        labels=("tissue",),
        processing_spacing=4.0,
        output_spacing=0.5,
        shape=(1024, 1024),
        backend='asap',
        full_coverage=False,
        offset=(0,0),
        callbacks=None,
    ):
        super().__init__(labels=labels, callbacks=callbacks)
        self._processing_spacing = processing_spacing
        self._output_spacing = output_spacing
        self._shape = np.array(shape)
        self._backend = backend
        self._offset = offset
        self._np_check_tissue = np.all if full_coverage else np.any

    def get_available_labels(opened_annotation: Any) -> Labels:
        return Labels.create({"tissue": 1})

    def _parse(self, path):
        mask = WholeSlideImage(path, backend=self._backend)

        size = self._shape[0]
        ratio = self._processing_spacing / self._output_spacing

        y_offset = int(self._offset[1] // ratio)
        x_offset = int(self._offset[0] // ratio)

        np_mask = mask.get_slide(self._processing_spacing).squeeze()
        shape = np.array(np_mask.shape)

        new_shape = shape + size // ratio - shape % (size // ratio)
        new_mask = np.zeros(new_shape.astype("int"), dtype="uint8")
        new_mask[: shape[0]-y_offset, : shape[1]-x_offset] = np_mask[y_offset:, x_offset:]

        for annotation in self._get_annotations(new_mask, size, ratio):
            yield annotation

        mask.close()
        mask = None
        del mask

    def _get_annotations(self, new_mask, size, ratio):
        region_index = -1
        blocks = block(new_mask, int(size // ratio), int(size // ratio))
        for y in range(new_mask.shape[0] // (int(size // ratio))):
            for x in range(new_mask.shape[1] // int((size // ratio))):
                region_index += 1
                if not self._np_check_tissue(blocks[region_index]):
                    continue

                box = self._get_coordinates((x * size)+self._offset[0], (y * size)+self._offset[1], size, size)
                yield {
                    "coordinates": np.array(box),
                    "label": {"name": "tissue", "value": 1},
                }

    def _get_coordinates(self, x_pos, y_pos, x_shift, y_shift) -> List:
        box = geometry.box(x_pos, y_pos, x_pos + x_shift, y_pos + y_shift)
        return np.array(box.exterior.xy).T.tolist()

    def _check_mask(self, mask_patch):
        if np.any(mask_patch):
            return np.unique(mask_patch, return_counts=True)
        return None, None


class CloudAnnotationParser(WholeSlideAnnotationParser):
    ...