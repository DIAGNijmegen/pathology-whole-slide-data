from copy import deepcopy
from typing import Iterable
import numpy as np

def get_buffer_shape(builds):
    batch_shape = builds['batch_shape']

    if isinstance(batch_shape._spacing, Iterable) and len(batch_shape._spacing) > 1:
        x_shape = (batch_shape.batch_size, len(batch_shape._spacing)) + tuple(batch_shape.shape[0])
    else:
        x_shape = (batch_shape.batch_size,) + tuple(batch_shape.shape)

    if batch_shape.y_shape is None:
        y_shape = x_shape[:-1]
        return batch_shape.batch_size, (x_shape, y_shape)

    y_shape = (batch_shape.batch_size,) + batch_shape.y_shape

    return batch_shape.batch_size, (x_shape, y_shape)