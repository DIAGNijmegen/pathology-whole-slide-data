from copy import deepcopy


def get_buffer_shape(config_builder):
    batch_shape = (
        deepcopy(config_builder)["training"]["batch_shape"].build({'wholeslidedata': config_builder['default']}).cast()
    )

    x_shape = (batch_shape.batch_size,) + batch_shape.shape
    if batch_shape.y_shape is None:
        return batch_shape.batch_size, (x_shape, x_shape[:-1])

    y_shape = (batch_shape.batch_size,) + batch_shape.y_shape
    
    return batch_shape.batch_size, (x_shape, y_shape)