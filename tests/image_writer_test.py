from pathlib import Path

import pytest

from wholeslidedata.annotation.wholeslideannotation import WholeSlideAnnotation
from wholeslidedata.image.wholeslideimage import WholeSlideImage
from wholeslidedata.interoperability.asap.backend import AsapWholeSlideImageBackend
from wholeslidedata.interoperability.asap.imagewriter import (
    WholeSlideImageWriter,
    WholeSlideMaskWriter,
    write_mask,
)
from wholeslidedata.iterators.patchiterator import (
    PatchConfiguration,
    create_patch_iterator,
)


@pytest.fixture
def wsi():
    return WholeSlideImage(
        "/tmp/TCGA-21-5784-01Z-00-DX1.tif", backend=AsapWholeSlideImageBackend
    )


def test_write_image(wsi: WholeSlideImage):
    output_path = Path("/tmp/imageat32.tif")
    wsi_writer = WholeSlideImageWriter()
    wsi_writer.write(
        output_path,
        wsi.get_real_spacing(32),
        wsi.get_shape_from_spacing(32),
        tile_shape=(512, 512, 3),
    )

    with create_patch_iterator(
        "/tmp/TCGA-21-5784-01Z-00-DX1.tif",
        patch_configuration=PatchConfiguration(spacings=(32.0,)),
    ) as iterator:
        for patch, info in iterator:
            wsi_writer.write_tile(patch)

    wsi_writer.finishImage()
    wsi_new = WholeSlideImage(output_path, backend=AsapWholeSlideImageBackend)
    assert round(wsi_new.spacings[0], 4) == round(wsi.get_real_spacing(32), 4)
    output_path.unlink()


def test_write_mask(wsi: WholeSlideImage):
    output_path = Path("/tmp/imageat32gray.tif")
    wsi_writer = WholeSlideMaskWriter()
    wsi_writer.write(
        output_path,
        wsi.get_real_spacing(32),
        wsi.get_shape_from_spacing(32),
        tile_shape=(512, 512),
    )
    with create_patch_iterator(
        "/tmp/TCGA-21-5784-01Z-00-DX1.tif",
        patch_configuration=PatchConfiguration(spacing=32.0),
    ) as iterator:
        for patch, info in iterator:
            r, g, b = patch[:, :, 0], patch[:, :, 1], patch[:, :, 2]
            gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
            wsi_writer.write_tile(gray)

    wsi_writer.finishImage()
    wsi_new = WholeSlideImage(output_path, backend=AsapWholeSlideImageBackend)
    assert round(wsi_new.spacings[0], 4) == round(wsi.get_real_spacing(32), 4)
    output_path.unlink()


def test_write_mask(wsi: WholeSlideImage):
    wsa = WholeSlideAnnotation("/tmp/TCGA-21-5784-01Z-00-DX1.xml")
    write_mask(wsi, wsa, 0.5)

    with pytest.warns(UserWarning) as record:
        write_mask(wsi, wsa, 0.5)
        assert len(record) == 1
        assert (
            record[0].message.args[0]
            == "Mask output path already exist: /tmp/TCGA-21-5784-01Z-00-DX1_gt_mask.tif"
        )

    Path("/tmp/TCGA-21-5784-01Z-00-DX1_gt_mask.tif").unlink()
