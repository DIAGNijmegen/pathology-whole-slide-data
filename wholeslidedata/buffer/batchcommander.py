from collections import deque
from wholeslidedata.samplers.batchreferencesampler import BatchReferenceSampler
from concurrentbuffer.commander import Commander


class BatchCommander(Commander):
    def __init__(self, config_builder, mode, reset_index=None):
        self._config_builder = config_builder
        self._mode = mode
        self._batch_reference_sampler = None
        self._reset_index = reset_index
        self._index = 0

    def build(self):
        mode = self._mode
        self._index = 0
        build = self._config_builder.build_instances()
        self._batch_reference_sampler = BatchReferenceSampler(
            dataset=build["wholeslidedata"][mode]["dataset"],
            batch_size=build["wholeslidedata"][mode]["batch_shape"].batch_size,
            label_sampler=build["wholeslidedata"][mode]["label_sampler"],
            annotation_sampler=build["wholeslidedata"][mode]["annotation_sampler"],
        )

    def create_message(self) -> dict:
        if self._reset_index is not None and (self._index % self._reset_index == 0):
            self._batch_reference_sampler.reset()
        sample_references = self._batch_reference_sampler.batch()
        message = {
            "mode": self._mode,
            "sample_references": sample_references,
            "index": self._index,
        }
        self._index += 1  
        return message
