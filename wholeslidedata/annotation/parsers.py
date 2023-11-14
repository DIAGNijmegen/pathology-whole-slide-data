from wholeslidedata.interoperability.asap.parser import AsapAnnotationParser
from wholeslidedata.interoperability.qupath.parser import QuPathAnnotationParser
from wholeslidedata.interoperability.virtum.parser import VirtumAsapAnnotationParser
from wholeslidedata.annotation.parser import WholeSlideAnnotationParser, MaskAnnotationParser

DEFAULT_PARSERS = {
    ".geojson": QuPathAnnotationParser,
    ".json": WholeSlideAnnotationParser,
    ".xml": AsapAnnotationParser,
    ".tif": MaskAnnotationParser,
    ".tiff": MaskAnnotationParser,
}


PARSERS = {
    'wsa': WholeSlideAnnotationParser,
    'mask': MaskAnnotationParser,
    'asap': AsapAnnotationParser,
    'virtum-asap': VirtumAsapAnnotationParser,
}