from dataclasses import dataclass
from pathlib import Path
from typing import List, Union
import numpy as np

import yaml
from wholeslidedata.mode import WholeSlideMode
from wholeslidedata.source.files import WholeSlideFile


class NoSourceFilesInFolderError(Exception):
    ...


class NonExistentModeInYamlSource(Exception):
    ...


def factory_sources_from_paths(
    cls: Union[str, type],
    mode: Union[str, WholeSlideMode],
    paths: List[str],
    filters: List[str],
    excludes: List[str],
    **kwargs,
):
    files = []
    paths = set(paths)
    for path in paths:
        path = str(path)
        if any([exclude in path for exclude in excludes]):
            continue
        if filters and not any([filter in path for filter in filters]):
            continue
        files.append(cls(mode=mode, path=path, **kwargs))
    return files


def factory_sources_from_path(file_type: str, mode: str, path: str, **kwargs):
    class_type = WholeSlideFile.get_registrant(file_type)
    sources = factory_sources_from_paths(class_type, mode, [path], [], [], **kwargs)
    if sources == []:
        raise ValueError(f"not a valid source {path}")
    return sources


def whole_slide_files_from_folder_factory(
    folder: Union[str, Path],
    file_type: Union[str, type],
    mode: str = "default",
    filters: List[str] = (),
    excludes: List[str] = (),
    recursive=False,
    **kwargs,
):

    class_type = WholeSlideFile.get_registrant(file_type)
    all_sources = []
    folder = Path(folder)
    for extension in class_type.EXTENSIONS.names():
        paths = (
            folder.rglob("*" + extension)
            if recursive
            else folder.glob("*" + extension)
        )
        sources = factory_sources_from_paths(
            class_type, mode, paths, filters, excludes, **kwargs
        )
        all_sources.extend(sources)

    if all_sources == []:
        raise NoSourceFilesInFolderError(class_type, filters, excludes, folder)
    return all_sources


def yaml_from_sources_factory(root_folder: str, class_folders: List[str], wsa_filetype: str, wsi_filetype: str,
                              output_path: str = "data.yml", excludes: List[str] = None, percentage: float = 0.3,
                              train_split=1.0):
    """
    Creates a yaml file to be used in the user_config.yaml as yaml_source. Allows for easy testing by using only a
    percentage of the original dataset.
    """
    folder = Path(root_folder)
    yaml_file = {"training": [], "validation": []}
    for class_folder in class_folders:
        wsis = list(folder.rglob(f"{class_folder}/*." + wsi_filetype))
        for i in range(int(len(wsis) * percentage)):
            wsi = str(wsis[i])
            wsa = str(wsi).strip(wsi_filetype) + f"{wsa_filetype}"
            if any(ex in wsi for ex in excludes or []) or not os.path.isfile(wsa):
                continue

            mode = np.random.choice(["training", "validation"], p=[train_split, 1 - train_split])
            yaml_file[mode].append({"wsi": {"path": wsi}, "wsa": {"path": wsa}})

    with open(output_path, 'w') as outfile:
        yaml = YAML()
        yaml.indent(sequence=4, offset=2)
        yaml.dump(yaml_file, outfile)


def sources_from_yaml_factory(
        yaml_source: Union[str, dict],
        file_type: str,
        mode: str = "default",
        filters=[],
        excludes=[],
        **kwargs,
):
    class_type = WholeSlideFile.get_registrant(file_type)

    data = {}

    if isinstance(yaml_source, dict):
        data = yaml_source
    elif isinstance(yaml_source, str):
        with open(yaml_source) as file:
            data = yaml.load(file, Loader=yaml.FullLoader)

    paths = []
    if mode not in data:
        raise NonExistentModeInYamlSource(
            f"mode '{mode}' not in data {data.keys()} in: {yaml_source}"
        )

    for item in data[mode]:
        if file_type in item:
            paths.append(item[file_type].pop("path"))
            kwargs.update(item[file_type])

    return factory_sources_from_paths(
        class_type, mode, paths, filters, excludes, **kwargs
    )
    


def factory_sources_from_json():
    pass


def factory_sources_from_csv():
    pass


import os
import yaml


def copy_from_yml(data_config, copy_path, modes=('training', 'validation'), file_types=('wsi', 'wsa')):
    data = []
    for mode in modes:
        for file_type in file_types:
            data.extend(sources_from_yaml_factory(data_config, file_type, mode=mode))
    for d in data:
        d.copy(copy_path)