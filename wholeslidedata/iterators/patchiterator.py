from multiprocessing import Queue

import numpy as np
from concurrentbuffer.iterator import BufferIterator, buffer_iterator_factory

from wholeslidedata.buffer.patchcommander import (
    SlidingPatchCommander,
    PatchConfiguration,
)
from wholeslidedata.buffer.patchproducer import PatchProducer


class PatchBufferIterator(BufferIterator):
    def __init__(self, buffer_factory, info_queue, size):
        self._size = size
        self._index = 0
        self._info_queue = info_queue
        super().__init__(buffer_factory)

    def __len__(self):
        return self._size

    def __next__(self):
        if self._index == len(self):
            self._index = 0
            raise StopIteration()
        self._index += 1
        return *tuple(map(np.squeeze, super().__next__())), self._info_queue.get()

    def reset(self):
        self._buffer_factory._commander.reset()


def create_patch_iterator(
    image_path,
    mask_path=None,
    patch_configuration=PatchConfiguration(),
    commander_class=SlidingPatchCommander,
    producer_class=PatchProducer,
    backend="asap",
    context="fork",
    cpus=1,
    producer_hooks=(),
):
    commander = commander_class(
        image_path=image_path,
        backend=backend,
        patch_configuration=patch_configuration,
        mask_path=mask_path,
    )

    producer = producer_class(
        image_path=image_path,
        mask_path=mask_path,
        backend=backend,
        producer_hooks=producer_hooks,
    )

    buffer_iterator = buffer_iterator_factory(
        cpus=cpus,
        buffer_shapes=commander.shapes,
        commander=commander,
        producer=producer,
        context=context,
        deterministic=True,
        buffer_dtype=np.uint8,
        info_queue=commander.info_queue,
        size=len(commander),
        buffer_iterator_class=PatchBufferIterator,
    )
    return buffer_iterator
