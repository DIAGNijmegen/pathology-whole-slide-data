from pytest_cov.embed import cleanup_on_sigterm

from wholeslidedata.iterators.patchiterator import (PatchConfiguration,
                                                    create_patch_iterator)

cleanup_on_sigterm()


def test_patch_iterator():
    patch_configuration = PatchConfiguration(patch_shape=(1024,1024,3),
                                            spacings=(0.5,),
                                            overlap=(0,0),
                                            offset=(0,0),
                                            center=False)

    with create_patch_iterator(image_path='/tmp/TCGA-21-5784-01Z-00-DX1.tif',
                            patch_configuration=patch_configuration,
                            cpus=4,
                            backend='openslide') as patch_iterator:
        
        print(f"Number of patches {len(patch_iterator)}\n")
        assert len(patch_iterator) == 900
        for idx, (patch, info) in enumerate(patch_iterator):
            pass


def test_patch_iterator_with_mask():
    patch_configuration = PatchConfiguration(patch_shape=(1024,1024,3),
                                            spacings=(0.5,),
                                            overlap=(0,0),
                                            offset=(0,0),
                                            center=False)

    with create_patch_iterator(image_path='/tmp/TCGA-21-5784-01Z-00-DX1.tif',
                            mask_path='/tmp/TCGA-21-5784-01Z-00-DX1_tb_mask.tif',
                            patch_configuration=patch_configuration,
                            cpus=4,
                            backend='asap') as patch_iterator:
        
        print(f"Number of patches {len(patch_iterator)}\n")
        assert len(patch_iterator) == 352
        for idx, (patch, mask, info) in enumerate(patch_iterator):
            pass
