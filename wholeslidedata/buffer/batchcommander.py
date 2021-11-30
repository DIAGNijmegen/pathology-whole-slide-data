import copy
from queue import Empty

from concurrentbuffer.commander import Commander

MESSAGE_MODE_IDENTIFIER = "mode"
MESSAGE_SAMPLE_REFERENCES_IDENTIFIER = "sample_references"
MESSAGE_INDEX_IDENTIFIER = "index"


class BatchCommander(Commander):
    def __init__(
        self, config_builder, mode, reset_index=None, update_queue=None, info_queue=None
    ):
        self._config_builder = config_builder
        self._mode = mode
        self._batch_reference_sampler = None
        self._reset_index = reset_index
        self._index = 0
        self._update_queue = update_queue
        self._info_queue = info_queue

    def build(self):
        mode = self._mode
        self._index = 0
        build = self._config_builder.build_instances()
        self._batch_reference_sampler = build["wholeslidedata"][mode]["batch_reference_sampler"]

    def create_message(self) -> dict:
        self._update()
        self._reset()

        sample_references = self._batch_reference_sampler.batch()
        message = {
            MESSAGE_MODE_IDENTIFIER: self._mode,
            MESSAGE_SAMPLE_REFERENCES_IDENTIFIER: sample_references,
            MESSAGE_INDEX_IDENTIFIER: self._index,
        }
        if self._info_queue:
            self._info_queue.put(copy.deepcopy(message))
        self._index += 1
        return message

    def _update(self):
        if self._update_queue is None:
            return

        try:
            while True:
                self._batch_reference_sampler.update(self._update_queue.get(False))
        except Empty:
            pass

    def _reset(self):
        if self._reset_index is None:
            return

        if self._index % self._reset_index == 0:
            self._batch_reference_sampler.reset()
