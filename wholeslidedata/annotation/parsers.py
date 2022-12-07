from wholeslidedata.interoperability.asap.parser import AsapAnnotationParser
from wholeslidedata.interoperability.virtum.parser import VirtumAsapAnnotationParser
from wholeslidedata.interoperability.s3.parser import S3AsapAnnotationParser
from wholeslidedata.annotation.parser import WholeSlideAnnotationParser, MaskAnnotationParser

PARSERS = {
    'wsa': WholeSlideAnnotationParser,
    'mask': MaskAnnotationParser,
    'asap': AsapAnnotationParser,
    'virtum-asap': VirtumAsapAnnotationParser,
    's3asap': S3AsapAnnotationParser,
}