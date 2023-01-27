from pathlib import Path
from typing import Union

from sourcelib.file import File

from wholeslidedata.annotation.wholeslideannotation import WholeSlideAnnotation
from wholeslidedata.data.extensions import (
    WHOLE_SLIDE_ANNOTATION_EXTENSIONS,
    WHOLE_SLIDE_IMAGE_EXTENSIONS,
)
from wholeslidedata.image.wholeslideimage import WholeSlideImage
from wholeslidedata.data.mode import WholeSlideMode


class WholeSlideImageFile(File):

    EXTENSIONS = WHOLE_SLIDE_IMAGE_EXTENSIONS
    IDENTIFIER = "wsi"

    def __init__(
        self,
        mode: Union[str, WholeSlideMode],
        path: Union[str, Path],
        image_backend: str = None,
    ):
        super().__init__(path=path, mode=mode)
        self._image_backend = image_backend

    def copy(self, destination_folder) -> None:
        destination_folder = Path(destination_folder) / "images"
        super().copy(destination_folder=destination_folder)

    def open(self):
        return WholeSlideImage(self.path, self._image_backend)


class WholeSlideAnnotationFile(File):

    EXTENSIONS = WHOLE_SLIDE_ANNOTATION_EXTENSIONS
    IDENTIFIER = "wsa"

    def __init__(
        self, mode: Union[str, WholeSlideMode], path: str, annotation_parser: str = None
    ):
        super().__init__(path=path, mode=mode)
        self._annotation_parser = annotation_parser

    def open(self, labels=None, spacing=None):
        return WholeSlideAnnotation(
            self.path, spacing=spacing, labels=labels, parser=self._annotation_parser
        )

    def copy(self, destination_folder) -> None:
        destination_folder = Path(destination_folder) / "annotations"
        super().copy(destination_folder=destination_folder)
