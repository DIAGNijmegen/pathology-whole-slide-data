from collections import UserDict
from pathlib import Path
from typing import Callable, List
from wholeslidedata.source.files import File
import warnings

def stem_file_associater(file: File):
    return file.path.stem

class StemSplitterAssociater:
    def __init__(self, split_symbols: tuple):
        self._split_symbols = split_symbols

    def __call__(self, file: File):
        association_name = file.path.stem
        for split_symbol in self._split_symbols:
            association_name = association_name.split(split_symbol)[0]
        return association_name

class AnyOneAssociater:
    def __call__(self, file: File):
        return 'AnyOneAssociater'
        
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

    def add_file(self, file: Path, associater: Callable, exact_match, required):
        file_key = self._associate(file, associater, exact_match)
        if file_key is None and not required:
            return
        self[file_key].add_file(file)

    def _associate(self, file: Path, associater: Callable,exact_match):
        file_association_key = associater(file)
        for file_key in self:
            if exact_match:
                if file_key == file_association_key:
                    return file_key
            elif file_key in file_association_key:
                return file_key

def associate_files(
    files1: List,
    files2: List,
    association: Associations = None,
    associator: Callable = stem_file_associater,
    exact_match=False,
) -> Associations:

    if association is None:
        association = Associations()

    for file1 in files1:
        file_key = associator(file1)
        association.add_file_key(file_key=file_key)
        association.add_file(file=file1, associater=associator, exact_match=exact_match, required=True)

    for file2 in files2:
        association.add_file(file=file2, associater=associator, exact_match=exact_match, required=False)

    # remove unpaired
    remove_keys = []
    for file_key, files in association.items():
        if len(list(files.keys())) <= 1:
            remove_keys.append(file_key)
            
    for remove_key in remove_keys:
        warnings.warn(f'Could not find matching image and annoation for key: {remove_key}')
        del association[remove_key]

    return association
