from wholeslidedata.interoperability.asap.parser import AsapAnnotationParser
from wholeslidedata.interoperability.virtum.parser import VirtumAsapAnnotationParser
from wholeslidedata.annotation.parser import WholeSlideAnnotationParser, MaskAnnotationParser

DEFAULT_PARSERS = {
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