import numpy as np
from concurrentbuffer.producer import Producer
from wholeslidedata.samplers.utils import atleast_4d


class BatchProducer(Producer):
    def __init__(self, config_builder, mode, reset_index=None):
        self._config_builder = config_builder
        self._mode = mode
        self._batch_sampler = None

        self._resets = 0
        self._reset_index = reset_index

    def build(self):
        build = self._config_builder.build_instances()
        self._batch_sampler = build["wholeslidedata"][self._mode]["batch_sampler"]
        return self._batch_sampler

    def create_data(self, message: dict) -> np.ndarray:
        index = message["index"]
        if self._reset_index is not None and (
            index // self._reset_index > self._resets
        ):
            self._batch_sampler.reset()
            self._resets += 1
        x_batch, y_batch = self._batch_sampler.batch(message["sample_references"])
        x_batch = np.array(x_batch)
        y_batch = atleast_4d(np.array(y_batch))
        packed_data = np.zeros(((2,) + x_batch.shape[:-1]) + (10,))
        packed_data[0][..., : x_batch.shape[-1]] = x_batch
        packed_data[1][..., : y_batch.shape[-1]] = y_batch
        return packed_data
