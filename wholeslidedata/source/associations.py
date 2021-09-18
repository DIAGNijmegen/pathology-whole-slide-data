from collections import UserDict
from pathlib import Path
from typing import Callable, List
from wholeslidedata.source.files import File
from dataclasses import dataclass

def stem_file_associater(file: File):
    return file.path.stem


class AssociatedFiles(UserDict):
    def __init__(self, file_key):
        self._file_key = file_key
        super().__init__(dict())

    def add_file(self, file):
        self.setdefault(type(file), []).append(file)


class Associations(UserDict):
    def __init__(self):
        super().__init__(dict())

    def add_file_key(self, file_key: str):
        self.setdefault(file_key, AssociatedFiles(file_key))

    def add_file(self, file: Path, associater: Callable, required):
        file_key = self._associate(file, associater)
        if file_key is None and not required:
            return
        self[file_key].add_file(file)

    def _associate(self, file: Path, associater: Callable):
        file_association_key = associater(file)
        for file_key in self:
            if file_key in file_association_key:
                return file_key

def associate_files(
    files1: List,
    files2: List,
    association: Associations = None,
    associator: Callable = stem_file_associater,
) -> Associations:

    if association is None:
        association = Associations()

    for file1 in files1:
        file_key = associator(file1)
        association.add_file_key(file_key=file_key)
        association.add_file(file=file1, associater=associator, required=True)

    for file2 in files2:
        association.add_file(file=file2, associater=associator, required=False)

    return association
