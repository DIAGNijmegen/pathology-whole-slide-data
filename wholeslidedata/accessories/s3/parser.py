
import xml.etree.ElementTree as ET

from urllib.parse import urlparse

import boto3
from botocore.handlers import disable_signing

boto_resource = boto3.resource('s3')
boto_resource.meta.client.meta.events.register('choose-signer.s3.*', disable_signing)

from wholeslidedata.annotation.parser import AnnotationParser

from wholeslidedata.accessories.asap.parser import AsapAnnotationParser

from wholeslidedata.labels import Labels


class CloudAnnotationParser(AnnotationParser):

    @classmethod
    def get_boto_obj(cls, path):

        s3_url_parse = urlparse(path, allow_fragments=False)
        s3_bucket_name = s3_url_parse.netloc
        s3_path = s3_url_parse.path.lstrip('/')
        boto_obj = boto_resource.Object(s3_bucket_name, s3_path)

        return boto_obj


@AnnotationParser.register(("s3asap",))
class S3AsapAnnotationParser(CloudAnnotationParser, AsapAnnotationParser):

    # def __init__(
    #             self,
    #             path: [str]
    #             ) -> None:
    #     """
    #     """


    def _open_annotation(self, path):

        boto_obj = self.get_boto_obj(path)
        xmldata = boto_obj.get()["Body"].read().decode('utf-8')
        opened_annotation = ET.fromstring(xmldata)

        return opened_annotation



