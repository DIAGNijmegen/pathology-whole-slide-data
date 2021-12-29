from typing import Iterable

from wholeslidedata.configuration.config import WholeSlideDataConfiguration
from wholeslidedata.dataset import WholeSlideDataSet


def get_dataset(builds: dict, mode: str) -> WholeSlideDataSet:
    return builds[WholeSlideDataConfiguration.NAME][mode]["dataset"]


def get_buffer_shape(builds: dict, mode: str) -> tuple:
    batch_shape = builds[WholeSlideDataConfiguration.NAME][mode]["batch_shape"]

    if isinstance(batch_shape._spacing, Iterable) and len(batch_shape._spacing) > 1:
        x_shape = (batch_shape.batch_size, len(batch_shape._spacing)) + tuple(
            batch_shape.shape[0]
        )
    else:
        x_shape = (batch_shape.batch_size,) + tuple(batch_shape.shape)

    if batch_shape.y_shape is None:
        y_shape = x_shape[:-1]
        return batch_shape.batch_size, (x_shape, y_shape)

    y_shape = (batch_shape.batch_size,) + batch_shape.y_shape

    return batch_shape.batch_size, (x_shape, y_shape)
