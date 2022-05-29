import os
import pathlib
from pathlib import Path
from typing import Dict, Union

from creationism.configuration.config import Configuration
from creationism.configuration.extensions import SEARCH_PATHS, open_config
from creationism.utils import open_yaml
from wholeslidedata.configuration import config
from wholeslidedata.source.files import (WholeSlideAnnotationFile,
                                         WholeSlideImageFile)

_DEFAULT_MODES = ("default",)

@Configuration.register(("source",))
class SourceConfiguration(Configuration):
    NAME = "source"
    PRESETS_FOLDER = pathlib.Path(__file__).absolute().parent / "presets"
    CONFIG_PATH = pathlib.Path(__file__).absolute().parent / os.path.join(
        "config_files", "config.yml"
    )

    SEARCH_PATHS = ("", pathlib.Path(__file__).absolute().parent / "config_files",  pathlib.Path(config.__file__).absolute().parent / "config_files")

    def __init__(self, modes=_DEFAULT_MODES, search_paths=()):

        search_paths_ = self.__class__.SEARCH_PATHS + search_paths
        config_value = open_config(
            SourceConfiguration.CONFIG_PATH, search_paths=search_paths_
        )

        super().__init__(
            name=SourceConfiguration.NAME,
            modes=modes,
            config_value=config_value,
            search_paths=search_paths,
        )

def get_paths(user_config: Union[Path, Dict], mode='default', preset=None):
    presets = (preset, ) if preset is not None else ()
    builds = SourceConfiguration.build(
        user_config=user_config, modes=(mode,), presets=presets,
    )
    for key, association in builds['source'][mode]['associations'].items():
        image_file = association[WholeSlideImageFile][0]
        mask_file=  association[WholeSlideAnnotationFile][0]
        yield image_file.path, mask_file.path
        
def insert_paths_into_config(user_config, image_path, annotation_path):
    user_config_dict = open_yaml(user_config)
    user_config_dict['wholeslidedata']['default']['image_sources']['path'] = str(image_path)
    user_config_dict['wholeslidedata']['default']['annotation_sources']['path'] = str(annotation_path)
    return user_config_dict
