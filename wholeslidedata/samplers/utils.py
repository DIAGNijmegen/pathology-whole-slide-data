import numpy as np

def block(arr, nrows, ncols):
    if len(arr.shape) == 3:
        height, _, channels = arr.shape
        return (
            arr.reshape(height // nrows, nrows, -1, ncols, channels)
            .swapaxes(1, 2)
            .reshape(-1, nrows, ncols, channels)
        )
    elif len(arr.shape) == 2:
        height, _ = arr.shape
        return (
            arr.reshape(height // nrows, nrows, -1, ncols)
            .swapaxes(1, 2)
            .reshape(-1, nrows, ncols)
        )


def unblock(arr, h, w):
    _, nrows, ncols, channels = arr.shape
    return (
        arr.reshape(h // nrows, -1, nrows, ncols, channels)
        .swapaxes(1, 2)
        .reshape(h, w, channels)
    )


def one_hot_encoding(mask, label_map, ignore_zero=True):
    """Encodes mask into one hot encoding."""
    ncols = max(label_map.values()) + 1
    out = np.zeros((mask.size, ncols), dtype=np.uint8)
    out[np.arange(mask.size), mask.ravel()] = 1
    out.shape = mask.shape + (ncols,)
    if 0 in label_map.values() and not ignore_zero:
        return out
    return out[..., 1:]


def one_hot_decoding(mask, base=-1):
    """decode one hot encoding"""
    xs, ys, lbl = np.where(mask)
    new_mask = np.zeros((mask.shape[0], mask.shape[1]))
    new_mask[xs, ys] = lbl.astype(int) + 1
    return new_mask + base


def clean_weights(masks):
    return np.clip(np.sum(masks, axis=-1), 0, 1)


def shift_coordinates(coordinates, center_x, center_y, width, height, ratio):
    coordinates = np.array(coordinates, dtype="float")
    coordinates -= np.array([center_x, center_y], dtype="float")
    coordinates /= ratio
    coordinates += np.array([width // 2, height // 2])
    return coordinates


def normalize(input_):
    _type = type(input_)
    if _type == np.ndarray:
        return input_ / 255.0
    return _type(np.array(input_) / 255.0)


def crop_data(data, output_shape):

    if (data.shape[0] == output_shape[0]) and (data.shape[1] == output_shape[1]):
        return data

    cropx = (data.shape[0] - output_shape[0]) // 2
    cropy = (data.shape[1] - output_shape[1]) // 2

    if len(data.shape) == 2:
        return data[cropx:-cropx, cropy:-cropy]
    if len(data.shape) == 3:
        return data[cropx:-cropx, cropy:-cropy, :]
    if len(data.shape) == 4:
        cropx = (data.shape[1] - output_shape[0]) // 2
        cropy = (data.shape[2] - output_shape[1]) // 2
        return data[:, cropx:-cropx, cropy:-cropy, :]
    if len(data.shape) == 5:
        cropx = (data.shape[2] - output_shape[0]) // 2
        cropy = (data.shape[3] - output_shape[1]) // 2
        return data[:, :, cropx:-cropx, cropy:-cropy, :]


def resolve_detection_batch(y_batch):
    return y_batch[~np.all(y_batch == 0, axis=-1)]


def resolve_classification_batch(y_batch):
    return np.squeeze(y_batch)

