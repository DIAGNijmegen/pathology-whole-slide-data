import math
from multiprocessing import Queue

import numpy as np
from concurrentbuffer.iterator import BufferIterator

from wholeslidedata.buffer.batchcommander import BatchCommander
from wholeslidedata.buffer.batchproducer import BatchProducer
from wholeslidedata.buffer.utils import create_buffer_factory
from wholeslidedata.configuration.config import WholeSlideDataConfiguration
from wholeslidedata.configuration.utils import get_buffer_shape, get_dataset


class BatchIterator(BufferIterator):
    def __init__(
        self,
        buffer_factory,
        dataset,
        batch_size,
        redundant,
        index=0,
        stop_index=None,
        info_queue=None,
    ):
        self._dataset = dataset
        self._batch_size = batch_size
        self._redundant = redundant
        self._index = index
        self._stop_index = stop_index
        self._info_queue = info_queue

        super().__init__(buffer_factory)

    @property
    def batch_size(self):
        return self._batch_size

    @property
    def dataset(self):
        return self._dataset

    def __next__(self):
        if self._stop():
            raise StopIteration()

        x_batch, y_batch = super().__next__()

        if (
            self._stop_index is not None
            and self._index == self._stop_index - 1
            and self._redundant > 0
        ):
            x_batch = x_batch[: self._redundant]
            y_batch = y_batch[: self._redundant]

        if self._info_queue is not None:
            info = self._info_queue.get()
            return x_batch, y_batch, info
        return x_batch, y_batch

    def _stop(self) -> bool:
        if self._stop_index is None:
            return False

        if self._index == self._stop_index:
            self._index = 0
            return True

        self._index += 1
        return False

    def __len__(self):
        if self._stop_index is None:
            raise TypeError("Batch iterator has no len() because it is infinite")
        return self._stop_index


def get_number_of_batches(number_of_batches, total_annotations, batch_size):
    if number_of_batches == -1:
        number_of_batches = math.ceil(total_annotations / batch_size)
        redundant = batch_size - (total_annotations % batch_size)
        return number_of_batches, redundant

    if number_of_batches <= 0:
        raise ValueError("number of batches can only be -1, None or > 0")

    return number_of_batches, 0


def create_batch_iterator(
    user_config,
    mode,
    number_of_batches=None,
    index=0,
    update_samplers=False,
    return_info=True,
    search_paths=(),
    presets=(),
    cpus=1,
    context="fork",
    determinstic=True,
    buffer_dtype=np.uint16,
):
    config_builder = WholeSlideDataConfiguration.build(
        user_config=user_config, modes=(mode,), build_instances=False, presets=presets, search_paths=search_paths,
    )

    builds = WholeSlideDataConfiguration.build(
        user_config=user_config, modes=(mode,), presets=presets, search_paths=search_paths,
    )

    batch_size, buffer_shapes = get_buffer_shape(builds, mode)
    dataset = get_dataset(builds, mode)

    redundant = 0
    if number_of_batches is not None:
        number_of_batches, redundant = get_number_of_batches(
            number_of_batches=number_of_batches,
            total_annotations=dataset.annotation_counts,
            batch_size=batch_size,
        )

    update_queue = Queue() if update_samplers else None
    info_queue = Queue() if return_info else None

    batch_commander = BatchCommander(
        config_builder=config_builder,
        mode=mode,
        reset_index=number_of_batches,
        update_queue=update_queue,
        info_queue=info_queue,
    )

    batch_producer = BatchProducer(
        config_builder=config_builder,
        mode=mode,
        reset_index=number_of_batches,
        update_queue=update_queue,
    )

    buffer_factory = create_buffer_factory(
        cpus=cpus,
        batch_commander=batch_commander,
        batch_producer=batch_producer,
        context=context,
        deterministic=determinstic,
        buffer_shapes=buffer_shapes,
        buffer_dtype=buffer_dtype,
    )

    return BatchIterator(
        buffer_factory=buffer_factory,
        dataset=dataset,
        batch_size=batch_size,
        redundant=redundant,
        index=index,
        stop_index=number_of_batches,
        info_queue=info_queue,
    )
