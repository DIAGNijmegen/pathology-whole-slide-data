from wholeslidedata.samplers.utils import one_hot_encoding, fit_data, block_shaped
import numpy as np
from typing import Dict, Tuple


class SampleCallback:
    def __init__(self):
        pass

    def __call__(
        self, x_patch: np.ndarray, y_patch: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        return x_patch, y_patch

    def reset(self):
        pass


class BatchCallback:
    def __init__(self, *args, **kwargs):
        pass

    def __call__(
        self, x_batch: np.ndarray, y_batch: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        return x_batch, y_batch

    def reset(self):
        pass


class BlockShaped(SampleCallback):
    def __init__(self, nrows, ncols):
        self._nrows = nrows
        self._ncols = ncols

    def __call__(self, x_patch, y_patch):
        x_patches = block_shaped(x_patch, self._nrows, self._ncols)
        y_patches = block_shaped(y_patch, self._nrows, self._ncols)
        return x_patches, y_patches


class OneHotEncoding(SampleCallback):
    def __init__(self, labels):
        self._label_map = {label.name: label.value for label in labels}

    def __call__(self, x_patch, y_patch):
        y_patch = one_hot_encoding(y_patch, self._label_map)
        return x_patch, y_patch


class Reshape(SampleCallback):
    def __call__(self, x_patch, y_patch):
        shape = y_patch.shape
        y_patch = y_patch.reshape(shape[0] * shape[1], -1).squeeze()
        return x_patch, y_patch


class ChannelsFirst(SampleCallback):
    def __call__(self, x_patch, y_patch):
        x_patch = x_patch.transpose(2,0,1)
        return x_patch, y_patch

class FitOutput(SampleCallback):
    def __init__(self, output_shape):
        self._output_shape = output_shape

    def __call__(self, x_patch, y_patch):
        y_patch = self._fit_data(y_patch)
        return x_patch, y_patch

    def _fit_data(self, y_patch):
        # cropping
        if y_patch.shape != self._output_shape:
            y_patch = fit_data(y_patch, self._output_shape)
        # Reshape
        return y_patch


class DataAugmentation(BatchCallback):
    def __init__(self, data_augmentation_config):
        self._data_augmentation_config = data_augmentation_config

    def __call__(
        self, x_batch: np.ndarray, y_batch: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:

        return x_batch, y_batch


class Resolver(BatchCallback):
    def __init__(self, return_dict=False):
        self._return_dict = return_dict

    def __call__(self, x_batch: np.ndarray, y_batch: np.ndarray):
        return self._resolve(x_batch, y_batch)

    def _resolve(self, x, y):
        x = list(map(self._resolve_samples, x))
        y = list(map(self._resolve_samples, y))
        if self._return_dict:
            return {"x": x, "y": y}
        return x, y

    def _resolve_samples(self, samples):
        out_samples = []
        for _, shapes in samples.items():
            for _, shape in shapes.items():
                out_samples.append(shape)
                
        if len(out_samples) == 1:
            return out_samples[0]
        return out_samples



