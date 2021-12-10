from dataclasses import dataclass
from pathlib import Path
from typing import List, Union

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
import shutil
import yaml


def copy(path, destination_folder):
    out_path = os.path.join(destination_folder, os.path.basename(path))
    exists = os.path.exists(out_path)
    if exists:
        pass
    elif os.path.exists(path) and os.path.isdir(destination_folder):
        print(f"copy from: {path}\ncopy to: {destination_folder}\n...")
        shutil.copy2(path, destination_folder.rstrip("/"))
    else:
        raise ValueError(f"error copying source {path}, {destination_folder}")


def copy_from_yml(yaml_path, output_path):
    with open(yaml_path) as file:
        content = yaml.full_load(file)

    for mode, collection in content.items():
        print(f"copying {mode} files...")
        for item in collection:
            for source_type, source in item.items():
                print(f"copying {source_type}...")
                print(source, source['path'])
                copy(source['path'], output_path)