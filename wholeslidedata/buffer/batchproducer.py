import numpy as np
from concurrentbuffer.producer import Producer
from wholeslidedata.buffer.batchcommander import (
    MESSAGE_INDEX_IDENTIFIER,
    MESSAGE_MODE_IDENTIFIER,
    MESSAGE_SAMPLE_REFERENCES_IDENTIFIER,
)


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
        index = message[MESSAGE_INDEX_IDENTIFIER]
        sample_references = message[MESSAGE_SAMPLE_REFERENCES_IDENTIFIER]

        if self._reset_index is not None:
            if index // self._reset_index > self._resets:
                self._batch_sampler.reset()
                self._resets += 1

        x_batch, y_batch = self._batch_sampler.batch(sample_references)
        return np.array(x_batch, dtype=np.uint8), np.array(y_batch, dtype=np.uint8)
