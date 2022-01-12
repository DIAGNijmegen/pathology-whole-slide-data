import abc
from collections import UserDict
from dataclasses import dataclass
from pprint import pformat
from typing import Dict, Tuple

from wholeslidedata.annotation import utils as annotation_utils
from wholeslidedata.labels import Labels
from wholeslidedata.mode import WholeSlideMode
from wholeslidedata.source.associations import Associations
from wholeslidedata.source.files import WholeSlideAnnotationFile, WholeSlideImageFile


@dataclass(frozen=True)
class WholeSlideSampleReference:
    file_index: int
    file_key: str
    wsa_index: int
    annotation_index: int


class DataSet(UserDict):

    IMAGES_IDENTIFIER = "images"
    ANNOTATIONS_IDENTIFIER = "annotations"

    def __init__(
        self,
        mode,
        associations: Associations,
        labels: Labels = None,
        renamed_labels: Labels = None,
    ):
        self._mode = WholeSlideMode.create(mode)
        self._associations = associations
        self._labels = labels
        self._renamed_labels = renamed_labels

        self.data = self._open(self._associations)
        self._sample_references, self._all_sample_references, self._all_labels = self._init_samples(
            self.data
        )
        self._sample_labels = Labels.create(list(self._sample_references.keys()))

        self._check_samples()
        self._log()

    @property
    def mode(self):
        return self._mode

    @property
    def sample_references(self):
        return self._sample_references

    @property
    def sample_labels(self):
        return self._sample_labels

    def get_image_from_reference(self, sample_reference: WholeSlideSampleReference):
        return self[sample_reference.file_key]["images"][0]

    def get_wsa_from_reference(self, sample_reference: WholeSlideSampleReference):
        return self[sample_reference.file_key]["annotations"][
            sample_reference.wsa_index
        ]

    def get_annotation_from_reference(
        self, sample_reference: WholeSlideSampleReference
    ):
        return self.get_wsa_from_reference(sample_reference=sample_reference).annotations[
            sample_reference.annotation_index
        ]

    @abc.abstractmethod
    def _open(self, associations: Associations) -> dict:
        """[summary]

        Args:
            associations (Associations): [description]

        Raises:
            ValueError: [description]

        Returns:
            dict: [description]
        """

    @abc.abstractmethod
    def _init_samples(self, data: dict) -> dict:
        """[summary]

        Args:
            data (dict): [description]

        Returns:
            dict: [description]
        """

    def _check_samples(self):
        if not self._sample_references:
            raise ValueError(
                f"No samples found in {self.mode.name} DataSet: \n{pformat(self.annotations_per_label)}"
            )

    def _log(self):
        pass

class WholeSlideDataSet(DataSet):
    def __init__(
        self,
        mode,
        associations: Associations,
        labels: Labels = None,
        renamed_labels: Labels = None,
        load_images=True,
        copy_path=None,
    ):
        self._load_images = load_images
        self._copy_path = copy_path
        super().__init__(mode, associations, labels, renamed_labels)

    def _open(self, associations):
        data = dict()
        for file_key, associated_files in associations.items():
            data[file_key] = {
                WholeSlideDataSet.IMAGES_IDENTIFIER: dict(),
                WholeSlideDataSet.ANNOTATIONS_IDENTIFIER: dict(),
            }
            for wsi_index, wsi_file in enumerate(associated_files[WholeSlideImageFile]):
                data[file_key][WholeSlideDataSet.IMAGES_IDENTIFIER][
                    wsi_index
                ] = self._open_image(wsi_file)
            for wsa_index, wsa_file in enumerate(
                associated_files[WholeSlideAnnotationFile]
            ):
                data[file_key][WholeSlideDataSet.ANNOTATIONS_IDENTIFIER][
                    wsa_index
                ] = self._open_annotation(wsa_file)
        return data

    def _open_image(self, wsi_file: WholeSlideImageFile):
        if self._copy_path:
            wsi_file.copy(self._copy_path)
        if self._load_images:
            return wsi_file.open()
        return wsi_file.path

    def _open_annotation(self, wsa_file: WholeSlideAnnotationFile):
        if self._copy_path:
            wsa_file.copy(self._copy_path)
        return wsa_file.open(labels=self._labels, renamed_labels=self._renamed_labels)

    def _init_samples(self, data) -> Tuple:
        samples = {}
        all_samples = {}
        _all_labels = set()
        data = dict(sorted(data.items()))
        for file_index, (file_key, values) in enumerate(data.items()):
            for wsa_index, wsa in values[
                WholeSlideDataSet.ANNOTATIONS_IDENTIFIER
            ].items():
                for annotation in wsa.sampling_annotations:
                    samples.setdefault(annotation.label.name, []).append(
                        WholeSlideSampleReference(
                            file_index=file_index,
                            file_key=file_key,
                            wsa_index=wsa_index,
                            annotation_index=annotation.index,
                        )
                    )

                for annotation in wsa.annotations:
                    _all_labels.add(annotation.label)
                    all_samples.setdefault(annotation.label.name, []).append(
                        WholeSlideSampleReference(
                            file_index=file_index,
                            file_key=file_key,
                            wsa_index=wsa_index,
                            annotation_index=annotation.index,
                        )
                    )
        return samples, all_samples, Labels.create(_all_labels)

    def close_images(self):
        for image in self._images.values():
            image.close()
            del image
        self._images = {}

    @property
    def annotation_counts(self):
        _counts = []
        for values in self.data.values():
            for wsa in values[WholeSlideDataSet.ANNOTATIONS_IDENTIFIER].values():
                _counts.append(
                    annotation_utils.get_counts_in_annotations(wsa.annotations)
                )
        return sum(_counts)

    @property
    def annotations_per_label(self) -> Dict[str, int]:
        counts_per_label_ = {label.name: 0 for label in self._all_labels}
        for values in self.data.values():
            for wsa in values[WholeSlideDataSet.ANNOTATIONS_IDENTIFIER].values():
                for label, count in annotation_utils.get_counts_in_annotations(
                    wsa.annotations, labels=self._all_labels
                ).items():
                    if label in counts_per_label_:
                        counts_per_label_[label] += count
        return counts_per_label_

    @property
    def annotations_per_key(self):
        _counts_per_key = {}
        for file_key, values in self.data.items():
            _counts_per_key[file_key] = 0
            for wsa in values[WholeSlideDataSet.ANNOTATIONS_IDENTIFIER].values():
                _counts_per_key[file_key] += annotation_utils.get_counts_in_annotations(
                    wsa.annotations
                )
        return _counts_per_key

    @property
    def annotations_per_label_per_key(self):
        counts_per_label_per_key_ = {}
        for file_key, values in self.data.items():
            counts_per_label_per_key_[file_key] = {}
            for wsa in values[WholeSlideDataSet.ANNOTATIONS_IDENTIFIER].values():
                for label, count in annotation_utils.get_counts_in_annotations(
                    wsa.annotations, labels=self._all_labels
                ).items():
                    if label not in counts_per_label_per_key_[file_key]:
                        counts_per_label_per_key_[file_key][label] = 0
                    counts_per_label_per_key_[file_key][label] += count
        return counts_per_label_per_key_

    @property
    def pixels_count(self):
        _counts = []
        for values in self.data.values():
            for wsa in values[WholeSlideDataSet.ANNOTATIONS_IDENTIFIER].values():
                _counts.append(
                    annotation_utils.get_pixels_in_annotations(wsa.annotations)
                )
        return sum(_counts)

    @property
    def pixels_per_label(self) -> Dict[str, int]:
        counts_per_label_ = {label.name: 0 for label in self._all_labels}

        for values in self.data.values():
            for wsa in values[WholeSlideDataSet.ANNOTATIONS_IDENTIFIER].values():
                for label, count in annotation_utils.get_pixels_in_annotations(
                    wsa.annotations, labels=self._all_labels
                ).items():
                    if label in counts_per_label_:
                        counts_per_label_[label] += count
        return counts_per_label_

    @property
    def pixels_per_key(self):
        _counts_per_key = {}
        for file_key, values in self.data.items():
            _counts_per_key[file_key] = 0
            for wsa in values[WholeSlideDataSet.ANNOTATIONS_IDENTIFIER].values():
                _counts_per_key[file_key] += annotation_utils.get_pixels_in_annotations(
                    wsa.annotations
                )
        return _counts_per_key

    @property
    def pixels_per_label_per_key(self):
        counts_per_label_per_key_ = {}
        for file_key, values in self.data.items():
            counts_per_label_per_key_[file_key] = {}
            for wsa in values[WholeSlideDataSet.ANNOTATIONS_IDENTIFIER].values():
                for label, pixels in annotation_utils.get_pixels_in_annotations(
                    wsa.annotations, labels=self._all_labels
                ).items():
                    if label not in counts_per_label_per_key_[file_key]:
                        counts_per_label_per_key_[file_key][label] = 0
                    counts_per_label_per_key_[file_key][label] += pixels
        return counts_per_label_per_key_