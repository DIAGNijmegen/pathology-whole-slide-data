from creationism.configuration.config import Configuration
from creationism.configuration.extensions import SEARCH_PATHS, open_config
import pathlib
import os

_DEFAULT_MODES = ("training", "validation")

@Configuration.register(("wholeslidedata",))
class WholeSlideDataConfiguration(Configuration):
    NAME = "wholeslidedata"
    PRESETS_FOLDER = pathlib.Path(__file__).absolute().parent / "presets"
    CONFIG_PATH = pathlib.Path(__file__).absolute().parent / os.path.join(
        "config_files", "config.yml"
    )

    SEARCH_PATHS = ("", pathlib.Path(__file__).absolute().parent / "config_files")

    def __init__(self, modes=_DEFAULT_MODES, search_paths=()):

        search_paths_ = self.__class__.SEARCH_PATHS + search_paths
        config_value = open_config(
            WholeSlideDataConfiguration.CONFIG_PATH, search_paths=search_paths_
        )

        super().__init__(
            name=WholeSlideDataConfiguration.NAME,
            modes=modes,
            config_value=config_value,
            search_paths=search_paths,
        )