import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from shutil import copy2


from shutil import copytree
import os


@dataclass(frozen=True)
class SourceFileTransferError(Exception):
    source_path: Path
    destination_folder: Path

    def __post_init__(self):
        super().__init__(self._message())

    def _message(self):
        return f"""
        Can not copy {self.source_path} to {self.destination_folder} because {self.source_path} does not exists"""


def _print_copy(orginal_path, destination_path):
    if destination_path.exists():
        pass
        # print(f"Destination path '{destination_path}' already exists")
    else:
        print(
            f"Copied from '{orginal_path}'\nCopied to: '{destination_path.resolve()}'\n..."
        )


def _log_copy(original_path, destination_path):
    logger = logging.getLogger("sourcecopy")
    if not destination_path.exists():
        logger.info(f"Copied (from): {original_path}")
        logger.info(f"Copied (to): {destination_path}\n\n")
    else:
        logger.info(f"Output ({destination_path}) already exists")


def copy(
    source_path: Path, destination_folder: Path, verbose: bool = True, log: bool = True
) -> Optional[Path]:

    if not source_path.exists():
        SourceFileTransferError(source_path, destination_folder)

    destination_path = _initialize_destination_path(source_path, destination_folder)

    if verbose:
        _print_copy(orginal_path=source_path, destination_path=destination_path)

    if not destination_path.exists():
        _transfer(source_path, destination_path)

    if log:
        _log_copy(original_path=source_path, destination_path=destination_path)

    return destination_path


def _initialize_destination_path(source: Path, destination_folder: Path):
    destination_folder = Path(destination_folder)
    destination_folder.mkdir(parents=True, exist_ok=True)
    return destination_folder / source.name


def _transfer(source: Path, destination_path: Path):
    transfer_function = copytree if os.path.isdir(source) else copy2
    transfer_function(str(source), str(destination_path))
