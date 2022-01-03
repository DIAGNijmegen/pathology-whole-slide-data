from abc import abstractmethod
from copy import copy
from pathlib import Path
from typing import List, Union

from creationism.extension import Extension
from creationism.registration.factory import RegistrantFactory
from wholeslidedata.annotation.wholeslideannotation import WholeSlideAnnotation
from wholeslidedata.extensions import (
    FolderCoupledExtension,
    WholeSlideAnnotationExtension,
    WholeSlideImageExtension,
)
from wholeslidedata.image.wholeslideimage import WholeSlideImage
from wholeslidedata.mode import Mode, WholeSlideMode
from wholeslidedata.source.copy import copy as copy_source


class File(RegistrantFactory):

    EXTENSIONS = Extension
    MODES = Mode

    def __init__(
        self,
        mode: Union[str, Mode],
        path: Union[str, Path],
    ):
        self.mode = self.__class__.MODES.create(mode)
        self.path = Path(path)
        self.extension = self.__class__.EXTENSIONS.create(self.path.suffix)
        self.orginal_path = copy(path)

    @abstractmethod
    def open(self):
        ...

    @property
    def exists(self):
        return self.path.exists()

    def copy(self, destination_folder):
        self.path = copy_source(self.path, destination_folder)

    def __str__(self):
        return "Mode: " + str(self.mode.name) + " | Path: " + str(self.path)


class ImageFile(File):
    def __init__(self, mode, path, image_backend):
        super().__init__(mode, path)
        self._image_backend = image_backend


class AnnotationFile(File):
    def __init__(self, mode, path, annotation_parser):
        super().__init__(mode, path)
        self._annotation_parser = annotation_parser


class WholeSlideFile(File):
    MODES = WholeSlideMode


@WholeSlideFile.register(("wsi", "wholeslideimage"))
class WholeSlideImageFile(WholeSlideFile, ImageFile):

    EXTENSIONS = WholeSlideImageExtension

    def __init__(
        self, mode: Union[str, Mode], path: Union[str, Path], image_backend: str
    ):
        super().__init__(mode, path, image_backend)

    def copy(self, destination_folder) -> None:
        destination_folder = Path(destination_folder) / 'images'
        extension_name = self.path.suffix
        if WholeSlideImageExtension.is_extension(
            extension_name, FolderCoupledExtension
        ):
            folder = self.path.with_suffix("")
            copy_source(folder, destination_folder)
        super().copy(destination_folder=destination_folder)

    def open(self):
        return WholeSlideImage(self.path, self._image_backend)


@WholeSlideFile.register(("wsa", "wholeslideannotation"))
class WholeSlideAnnotationFile(WholeSlideFile, AnnotationFile):

    EXTENSIONS = WholeSlideAnnotationExtension

    def __init__(self, mode: Union[Mode, str], path: str, annotation_parser: str):
        super().__init__(mode, path, annotation_parser)

    def open(self, labels=None, renamed_labels=None):
        return WholeSlideAnnotation(
            self.path, labels, renamed_labels, self._annotation_parser
        )

    def copy(self, destination_folder) -> None:
        destination_folder = Path(destination_folder) / 'annotations'
        super().copy(destination_folder=destination_folder)