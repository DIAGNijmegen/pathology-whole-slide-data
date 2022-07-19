import xml.etree.ElementTree as ET
from urllib.parse import urlparse

import boto3
from botocore.handlers import disable_signing
from botocore.exceptions import ClientError

boto_resource = boto3.resource("s3")
boto_resource.meta.client.meta.events.register("choose-signer.s3.*", disable_signing)

from wholeslidedata.accessories.asap.parser import AsapAnnotationParser
from wholeslidedata.annotation.parser import AnnotationParser, CloudAnnotationParser


class S3AnnotationParser(CloudAnnotationParser):
    @classmethod
    def get_boto_obj(cls, path: str):
        s3_url_parse = urlparse(path, allow_fragments=False)
        s3_bucket_name = s3_url_parse.netloc
        s3_path = s3_url_parse.path.lstrip("/")
        boto_obj = boto_resource.Object(s3_bucket_name, s3_path)

        return boto_obj

    @classmethod
    def _path_exists(cls, path):
        try:
            s3_obj_status_code = cls.get_boto_obj(path).get()["ResponseMetadata"][
                "HTTPStatusCode"
            ]
        except ClientError:
            raise FileNotFoundError(
                f"Could not retreive boto object while retreiving status code for path: \n{path}"
            )

        if s3_obj_status_code == 200:
            return True

    @classmethod
    def _empty_file(cls, path: str):
        return False

@AnnotationParser.register(("s3asap",), recursive=True)
class S3AsapAnnotationParser(AsapAnnotationParser, S3AnnotationParser):
    def _open_annotation(self, path: str):

        boto_obj = self.get_boto_obj(path)
        xmldata = boto_obj.get()["Body"].read().decode("utf-8")
        opened_annotation = ET.fromstring(xmldata)

        return opened_annotation
