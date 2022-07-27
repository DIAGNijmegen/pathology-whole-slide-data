from multiprocessing import Queue

import numpy as np
from concurrentbuffer.iterator import BufferIterator, buffer_iterator_factory

from wholeslidedata.buffer.patchcommander import SlidingPatchCommander
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
        return super().__next__(), self._info_queue.get()

    def reset(self):
        self._buffer_factory._commander.reset()

def create_patch_iterator(
    image_path,
    spacing,
    cpus=1,
    context="fork",
    tile_shape=(512, 512, 3),
    backend="asap",
    commander_class=SlidingPatchCommander,
    producer_class=PatchProducer,
    **kwargs,
):
    info_queue = Queue()

    commander = commander_class(
        info_queue=info_queue,
        image_path=image_path,
        backend=backend,
        spacing=spacing,
        tile_shape=tile_shape,
        **kwargs,
    )
    producer = producer_class(
        image_path=image_path, tile_shape=tile_shape, backend=backend, **kwargs
    )

    buffer_iterator = buffer_iterator_factory(
        cpus=cpus,
        buffer_shapes=producer.shapes,
        commander=commander,
        producer=producer,
        context=context,
        deterministic=True,
        buffer_dtype=np.uint8,
        info_queue=info_queue,
        size=len(commander),
        buffer_iterator_class=PatchBufferIterator,
    )
    return buffer_iterator
