from pathlib import Path
from wholeslidedata.iterators.patchiterator import create_patch_iterator
from wholeslidedata.buffer.patchcommander import RandomPatchCommander

from pytest_cov.embed import cleanup_on_sigterm
cleanup_on_sigterm()


def test_patch_iterator():
    with create_patch_iterator(image_path='/tmp/TCGA-21-5784-01Z-00-DX1.tif', spacing=32.0) as patch_iterator:
        for patch in patch_iterator:
            pass


def test_patch_iterator_random():
    with create_patch_iterator(image_path='/tmp/TCGA-21-5784-01Z-00-DX1.tif', spacing=32.0, commander_class=RandomPatchCommander) as patch_iterator:
        for patch in patch_iterator:
            pass
