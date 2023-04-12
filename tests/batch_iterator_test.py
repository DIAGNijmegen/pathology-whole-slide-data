import os
from pathlib import Path

from pytest_cov.embed import cleanup_on_sigterm

from wholeslidedata.iterators.batchiterator import create_batch_iterator

cleanup_on_sigterm()


def test_batch_iterator():
    os.environ["TMP"] = "/tmp"
    with create_batch_iterator(
        user_config=Path(__file__).parent / "user_config.yml",
        mode="training",
        number_of_batches=5,
    ) as batch_iterator:
        for x_batch, y_batch, info in batch_iterator:
            pass
