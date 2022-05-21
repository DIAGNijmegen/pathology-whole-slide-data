import random

from wholeslidedata.samplers.utils import one_hot_encoding, fit_data, block_shaped
import numpy as np
from typing import Dict, Tuple

import skimage.color

class SampleCallback:
    """Pass through callback on samples"""

    def __init__(self):
        pass

    def __call__(
            self, x_patch: np.ndarray, y_patch: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        return x_patch, y_patch

    def reset(self):
        pass



class BatchCallback:
    """Pass through callback on batches"""

    def __init__(self, *args, **kwargs):
        pass

    def __call__(
            self, x_batch: np.ndarray, y_batch: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        return x_batch, y_batch

    def reset(self):
        pass


class BlockShaped(SampleCallback):
    """Reshapes samples into blocks"""

    def __init__(self, nrows, ncols):
        self._nrows = nrows
        self._ncols = ncols

    def __call__(self, x_patch, y_patch):
        x_patches = block_shaped(x_patch, self._nrows, self._ncols)
        y_patches = block_shaped(y_patch, self._nrows, self._ncols)
        return x_patches, y_patches


class OneHotEncoding(SampleCallback):
    """One-hot encodes y sample"""

    def __init__(self, labels, ignore_zero=True):
        self._ignore_zero = ignore_zero
        self._label_map = {label.name: label.value for label in labels}

    def __call__(self, x_patch, y_patch):
        y_patch = one_hot_encoding(y_patch, self._label_map, self._ignore_zero)
        return x_patch, y_patch


class Reshape(SampleCallback):
    """Flattens first and second dimension in y sample"""

    def __call__(self, x_patch, y_patch):
        shape = y_patch.shape
        y_patch = y_patch.reshape(shape[0] * shape[1], -1).squeeze()
        return x_patch, y_patch


class ChannelsFirst(SampleCallback):
    """Tranposes x sample from channels last to channels first"""

    def __call__(self, x_patch, y_patch):
        x_patch = x_patch.transpose(2, 0, 1)
        return x_patch, y_patch


class FitOutput(SampleCallback):
    """Crops y patch to fit output shape"""

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


class HedCallback(BatchCallback):
    def __init__(self, hem=0.02, eos=0.02, dab=0.02, probability=0.5):
        self._hem = hem
        self._eos = eos
        self._dab = dab
        self._probability = probability

    def __call__(self, x_batch: np.ndarray, y_batch: np.ndarray):
        batch_size = len(x_batch)
        
        probs = np.random.uniform(size=batch_size)
        if np.all(probs > self._probability):
            return x_batch, y_batch

        _type = type(x_batch)
        x_batch = np.array(x_batch)

        x_batch_hed = skimage.color.rgb2hed(x_batch / 255)

        h = np.random.uniform(low=-self._hem, high=self._hem, size=(batch_size,))
        e = np.random.uniform(low=-self._eos, high=self._eos, size=(batch_size,))
        d = np.random.uniform(low=-self._dab, high=self._dab, size=(batch_size,))

        h *= np.random.randint(2, size=(batch_size))
        e *= np.random.randint(2, size=(batch_size))
        d *= np.random.randint(2, size=(batch_size))

        for i, (hv, ev, db) in enumerate(zip(h, e, d)):
            if probs[i] > self._probability:
                continue
            x_batch_hed[i, ..., 0] += hv
            x_batch_hed[i, ..., 1] += ev
            x_batch_hed[i, ..., 2] += db

        ihc_rgb = skimage.color.hed2rgb(x_batch_hed)
        ihc = np.clip(a=ihc_rgb * 255, a_min=0, a_max=255)
        return _type(ihc), y_batch

class Resolver(BatchCallback):
    """Resolves shape of batch"""

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
