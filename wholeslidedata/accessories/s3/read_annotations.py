
import xml.etree.ElementTree as ET

from urllib.parse import urlparse

import boto3
from botocore.handlers import disable_signing

boto_resource = boto3.resource('s3')
boto_resource.meta.client.meta.events.register('choose-signer.s3.*', disable_signing)



class ReadAnnotationsFromS3():

    # def __init__(
    #             self,
    #             path: [str]
    #             ) -> None:
    #     """

    #     """

    def get_annotation_path_and_suffix(path):

        annotation_path = path
        annotation_path_suffix = '.xml'

        return annotation_path, annotation_path_suffix


    def return_opened_annotation(path):

        s3_url_parse = urlparse(path, allow_fragments=False)
        s3_bucket_name = s3_url_parse.netloc
        s3_path = s3_url_parse.path.lstrip('/')
        boto_obj = boto_resource.Object(s3_bucket_name, s3_path)
        xmldata = boto_obj.get()["Body"].read().decode('utf-8')
        opened_annotation = ET.fromstring(xmldata)

        return opened_annotation

