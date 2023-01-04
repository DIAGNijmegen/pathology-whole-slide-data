import math
from multiprocessing import Queue
from typing import Iterable

import numpy as np
from concurrentbuffer.iterator import BufferIterator
from concurrentbuffer.factory import create_buffer_factory
from dicfg.reader import ConfigReader
from dicfg.factory import build_config
from wholeslidedata.buffer.batchcommander import BatchCommander
from wholeslidedata.buffer.batchproducer import BatchProducer
from wholeslidedata.configuration import MAIN_CONFIG_PATH


class BatchIterator(BufferIterator):
    def __init__(
        self,
        buffer_factory,
        dataset,
        batch_size,
        batch_left,
        index=0,
        stop_index=None,
        info_queue=None,
    ):
        self._dataset = dataset
        self._batch_size = batch_size
        self._batch_left = batch_left
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
            and self._index == self._stop_index
            and self._batch_left > 0
        ):
            x_batch = x_batch[: self._batch_left]
            y_batch = y_batch[: self._batch_left]

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


def get_buffer_shape(batch_shape) -> tuple:
    if isinstance(batch_shape._spacing, Iterable) and len(batch_shape._spacing) > 1:
        x_shape = (batch_shape.batch_size, len(batch_shape._spacing)) + tuple(
            batch_shape.shape[0]
        )
    else:
        x_shape = (batch_shape.batch_size,) + tuple(batch_shape.shape)

    if batch_shape.y_shape is None:
        y_shape = x_shape[:-1]
        return batch_shape.batch_size, (x_shape, y_shape)

    y_shape = (batch_shape.batch_size,) + batch_shape.y_shape

    return (x_shape, y_shape)


def get_number_of_batches(number_of_batches, dataset, batch_size):

    batch_left = 0
    if number_of_batches is not None:
        total_annotations = 0
        for label_name in dataset.sample_labels.names:
            total_annotations += dataset.annotations_per_label[label_name]

        if number_of_batches == -1:
            number_of_batches = math.ceil(total_annotations / batch_size)
            # left over
            batch_left = total_annotations % batch_size
            return number_of_batches, batch_left

        if number_of_batches <= 0:
            raise ValueError("number of batches can only be -1, None or > 0")

        return number_of_batches, 0
    return number_of_batches, batch_left


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
    iterator_class=BatchIterator,
):

    config_reader = ConfigReader(
        name="wholeslidedata",
        main_config_path=MAIN_CONFIG_PATH,
        context_keys=(mode,),
        search_paths=search_paths,
    )
    config = config_reader.read(user_config=user_config, presets=presets)

    builds = build_config(config[mode])

    batch_shape = builds["batch_shape"]
    dataset = builds["dataset"]
    buffer_shapes = get_buffer_shape(batch_shape)
    number_of_batches, batch_left = get_number_of_batches(
        number_of_batches, dataset, batch_shape.batch_size
    )

    update_queue = Queue() if update_samplers else None
    info_queue = Queue() if return_info else None

    batch_commander = BatchCommander(
        config=config,
        mode=mode,
        reset_index=number_of_batches,
        update_queue=update_queue,
        info_queue=info_queue,
    )

    batch_producer = BatchProducer(
        config=config,
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

    return iterator_class(
        buffer_factory=buffer_factory,
        dataset=dataset,
        batch_size=batch_shape.batch_size,
        batch_left=batch_left,
        index=index,
        stop_index=number_of_batches,
        info_queue=info_queue,
    )
