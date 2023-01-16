from collections import UserDict
from dataclasses import dataclass
from enum import Enum
from pprint import pformat
from typing import Dict, Tuple

from sourcelib.associations import Associations

from wholeslidedata.annotation import utils as annotation_utils
from wholeslidedata.data.files import WholeSlideAnnotationFile, WholeSlideImageFile
from wholeslidedata.annotation.labels import Labels


@dataclass(frozen=True)
class WholeSlideSampleReference:
    file_index: int
    file_key: str
    wsa_index: int
    annotation_index: int


class WholeSlideDataSet(UserDict):

    IMAGES_KEY = "images"
    ANNOTATIONS_KEY = "annotations"

    def __init__(
        self,
        mode: Enum,
        associations: Associations,
        labels: Labels = None,
        load_images=True,
        copy_path=None,
    ):

        self._mode = mode
        self._load_images = load_images
        self._copy_path = copy_path
        self._associations = associations
        self._data = dict(sorted(self._open(self._associations, labels=labels).items()))
        self._labels = self._init_labels()
        self._sample_references = self._init_samples()
        self._sample_labels = Labels.create([label for label in self._labels if label.name in list(self._sample_references.keys())])
        
        if len(self._sample_references) == 0:
            raise ValueError(
                f"No samples found in {self.mode.name} DataSet: \n{pformat(self.annotations_per_label_per_key)}"
            )

        super().__init__(self._data)


    @property
    def mode(self):
        return self._mode

    @property
    def sample_references(self):
        return self._sample_references

    @property
    def labels(self):
        return self._labels
    
    @property
    def sample_labels(self):
        return self._sample_labels

    def get_wsi_from_reference(self, sample_reference: WholeSlideSampleReference):
        return self[sample_reference.file_key][self.__class__.IMAGES_KEY][0]

    def get_wsa_from_reference(self, sample_reference: WholeSlideSampleReference):
        return self[sample_reference.file_key][self.__class__.ANNOTATIONS_KEY][
            sample_reference.wsa_index
        ]

    def get_annotation_from_reference(
        self, sample_reference: WholeSlideSampleReference
    ):
        return self.get_wsa_from_reference(
            sample_reference=sample_reference
        ).annotations[sample_reference.annotation_index]

 

    def _open(self, associations, labels):
        data = dict()
        for file_key, associated_files in associations.items():
            data[file_key] = {
                self.__class__.IMAGES_KEY: dict(),
                self.__class__.ANNOTATIONS_KEY: dict(),
            }
            spacings = []
            for wsi_index, wsi_file in enumerate(associated_files[WholeSlideImageFile.IDENTIFIER]):
                image, spacing = self._open_image(wsi_file)
                data[file_key][self.__class__.IMAGES_KEY][
                    wsi_index
                ] = image
                spacings.append(spacing)
            for wsa_index, wsa_file in enumerate(
                associated_files[WholeSlideAnnotationFile.IDENTIFIER]
            ):
                data[file_key][self.__class__.ANNOTATIONS_KEY][
                    wsa_index
                ] = self._open_annotation(wsa_file, spacing=spacings[0], labels=labels)
        return data

    def _open_image(self, wsi_file: WholeSlideImageFile):
        if self._copy_path:
            wsi_file.copy(self._copy_path)

        wsi = wsi_file.open()
        spacing = wsi.spacings[0]
        
        if self._load_images:
            return wsi, spacing

        wsi.close()
        wsi = None
        del wsi
        return wsi_file, spacing

    def _open_annotation(self, wsa_file: WholeSlideAnnotationFile, labels, spacing=None):
        if self._copy_path:
            wsa_file.copy(self._copy_path)
        return wsa_file.open(spacing=spacing, labels=labels)

    def _init_labels(self):
        labels = []
        for values in self._data.values():
            for wsa in values[self.__class__.ANNOTATIONS_KEY].values():
                for annotation in wsa._annotations:
                    labels.append(annotation.label)
        return Labels.create(list(set(labels)))

    def _init_samples(self) -> Tuple:
        sample_references = {}
        for file_index, (file_key, values) in enumerate(self._data.items()):
            for wsa_index, wsa in values[self.__class__.ANNOTATIONS_KEY].items():
                for annotation in wsa.sampling_annotations:
                    sample_references.setdefault(annotation.label.name, []).append(
                        WholeSlideSampleReference(
                            file_index=file_index,
                            file_key=file_key,
                            wsa_index=wsa_index,
                            annotation_index=annotation.index,
                        )
                    )

        return sample_references

    @property
    def annotation_counts(self):
        _counts = []
        for values in self._data.values():
            for wsa in values[self.__class__.ANNOTATIONS_KEY].values():
                _counts.append(
                    annotation_utils.get_counts_in_annotations(wsa.annotations)
                )
        return sum(_counts)

    @property
    def counts_per_label(self) -> Dict[str, int]:
        _counts_per_label_ = {label.name: 0 for label in self._labels}
        for values in self._data.values():
            for wsa in values[self.__class__.ANNOTATIONS_KEY].values():
                for label, count in annotation_utils.get_counts_in_annotations(
                    wsa.annotations, labels=self._labels
                ).items():
                    if label in _counts_per_label_:
                        _counts_per_label_[label] += count
        return _counts_per_label_

    @property
    def counts_per_key(self):
        _counts_per_key = {}
        for file_key, values in self._data.items():
            _counts_per_key[file_key] = 0
            for wsa in values[self.__class__.ANNOTATIONS_KEY].values():
                _counts_per_key[file_key] += annotation_utils.get_counts_in_annotations(
                    wsa.annotations
                )
        return _counts_per_key

    @property
    def counts_per_label_per_key(self):
        _counts_per_label_per_key_ = {}
        for file_key, values in self._data.items():
            _counts_per_label_per_key_[file_key] = {}
            for wsa in values[self.__class__.ANNOTATIONS_KEY].values():
                for label, count in annotation_utils.get_counts_in_annotations(
                    wsa.annotations, labels=self._labels
                ).items():
                    if label not in _counts_per_label_per_key_[file_key]:
                        _counts_per_label_per_key_[file_key][label] = 0
                    _counts_per_label_per_key_[file_key][label] += count
        return _counts_per_label_per_key_

    @property
    def pixels_count(self):
        _counts = []
        for values in self._data.values():
            for wsa in values[self.__class__.ANNOTATIONS_KEY].values():
                _counts.append(
                    annotation_utils.get_pixels_in_annotations(wsa.annotations)
                )
        return sum(_counts)

    @property
    def pixels_per_label(self) -> Dict[str, int]:
        counts_per_label_ = {label.name: 0 for label in self._labels}

        for values in self._data.values():
            for wsa in values[self.__class__.ANNOTATIONS_KEY].values():
                for label, count in annotation_utils.get_pixels_in_annotations(
                    wsa.annotations, labels=self._labels
                ).items():
                    if label in counts_per_label_:
                        counts_per_label_[label] += count
        return counts_per_label_

    @property
    def pixels_per_key(self):
        _counts_per_key = {}
        for file_key, values in self._data.items():
            _counts_per_key[file_key] = 0
            for wsa in values[self.__class__.ANNOTATIONS_KEY].values():
                _counts_per_key[file_key] += annotation_utils.get_pixels_in_annotations(
                    wsa.annotations
                )
        return _counts_per_key

    @property
    def pixels_per_label_per_key(self):
        counts_per_label_per_key_ = {}
        for file_key, values in self._data.items():
            counts_per_label_per_key_[file_key] = {}
            for wsa in values[self.__class__.ANNOTATIONS_KEY].values():
                for label, pixels in annotation_utils.get_pixels_in_annotations(
                    wsa.annotations, labels=self._labels
                ).items():
                    if label not in counts_per_label_per_key_[file_key]:
                        counts_per_label_per_key_[file_key][label] = 0
                    counts_per_label_per_key_[file_key][label] += pixels
        return counts_per_label_per_key_
