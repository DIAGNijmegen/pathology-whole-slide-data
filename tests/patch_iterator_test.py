from pytest_cov.embed import cleanup_on_sigterm

from wholeslidedata.iterators.patchiterator import (PatchConfiguration,
                                                    create_patch_iterator)

cleanup_on_sigterm()


def test_patch_iterator():
    with create_patch_iterator(
        image_path="/tmp/TCGA-21-5784-01Z-00-DX1.tif",
        patch_configuration=PatchConfiguration(spacings=(32,)),
    ) as patch_iterator:
        for patch in patch_iterator:
            pass
