import numpy as np
from concurrentbuffer.producer import Producer
from dicfg.factory import build_config
from wholeslidedata.buffer.batchcommander import (
    MESSAGE_INDEX_IDENTIFIER,
    MESSAGE_MODE_IDENTIFIER,
    MESSAGE_SAMPLE_REFERENCES_IDENTIFIER,
)


class BatchProducer(Producer):
    def __init__(self, config, mode, reset_index=None, update_queue=None):
        self._config = config
        self._mode = mode
        self._batch_sampler = None

        self._resets = 0
        self._reset_index = reset_index
        self._update_queue = update_queue

    def build(self):
        builds = build_config(self._config[self._mode])
        self._batch_sampler = builds["batch_sampler"]

    def create_data(self, message: dict) -> np.ndarray:
        index = message[MESSAGE_INDEX_IDENTIFIER]
        sample_references = message[MESSAGE_SAMPLE_REFERENCES_IDENTIFIER]
        self._reset(index)
        batch = self._create_batch(sample_references)
        self._update(*batch)
        return batch

    def _create_batch(self, sample_references):
        x_batch, y_batch = self._batch_sampler.batch(sample_references)
        x_batch = np.array(x_batch)
        y_batch = np.array(y_batch)
        return x_batch, y_batch

    def _reset(self, index):
        if self._reset_index is None:
            return

        if index // self._reset_index > self._resets:
            self._batch_sampler.reset()
            self._resets += 1

    def _update(self, x_batch, y_batch):
        if self._update_queue is not None:
            self._update_queue.put((x_batch, y_batch), block=False)
