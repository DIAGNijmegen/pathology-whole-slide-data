from copy import deepcopy
from concurrentbuffer.iterator import BufferIterator, buffer_iterator_factory

from wholeslidedata.buffer.batchcommander import BatchCommander
from wholeslidedata.buffer.batchproducer import BatchProducer
from wholeslidedata.buffer.utils import get_buffer_shape
from wholeslidedata.configuration.config import WholeSlideDataConfiguration
from wholeslidedata.samplers.structures import BatchShape, Sample
from multiprocessing import Queue
import math

class BatchIterator(BufferIterator):
    def __init__(self, mode, builds, batch_size, redundant, index=0, stop_index=None, info_queue=None, *args, **kwargs):
        self._mode = mode
        self._builds = builds
        self._batch_size = batch_size
        self._redundant = redundant
        self._index = index
        self._stop_index = stop_index
        self._info_queue = info_queue

        super().__init__(*args, **kwargs)

    @property
    def batch_size(self):
        return self._batch_size
    
    @property
    def dataset(self):
        return self._builds['wholeslidedata'][self._mode]['dataset']
    
    
    def __next__(self):
        if self._stop():
            raise StopIteration()

        x_batch, y_batch = super().__next__()

        if self._stop_index is not None and self._index == self._stop_index-1 and self._redundant > 0:
            x_batch = x_batch[:self._redundant]
            y_batch = y_batch[:self._redundant]

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


def create_batch_iterator(
    user_config,
    mode,
    number_of_batches=None,
    update_samplers=False,
    return_info=True,
    presets=(),
    cpus=1,
    context="fork",
    determinstic=True,
    iterator_class=BatchIterator,
):
    config_builder = WholeSlideDataConfiguration.build(
        user_config=user_config, modes=(mode,), build_instances=False, presets=presets
    )

    builds = WholeSlideDataConfiguration.build(
        user_config=user_config, modes=(mode,), presets=presets
    )

 

    update_queue = Queue() if update_samplers else None
    info_queue = Queue() if return_info else None

   
    batch_size, buffer_shapes = get_buffer_shape(builds['wholeslidedata'][mode])

    total_annotations = builds['wholeslidedata'][mode]['dataset'].annotation_counts
    if number_of_batches == -1:
        number_of_batches = math.ceil(total_annotations / batch_size)
        redundant = batch_size - (total_annotations % batch_size)
    else:
        redundant = 0

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


    return buffer_iterator_factory(
        mode=mode,
        builds=builds,
        batch_size=batch_size,
        redundant=redundant,
        stop_index=number_of_batches,
        info_queue=info_queue,
        cpus=cpus,
        buffer_shapes=buffer_shapes,
        commander=batch_commander,
        producer=batch_producer,
        context=context,
        deterministic=determinstic,
        buffer_iterator_class=iterator_class,
    )


def create_sample(
    self, sample_data, image_path, label_name, index, point, pixel_spacing
):
    return Sample(
        sample_data,
        image_path,
        label_name,
        index,
        point,
        pixel_spacing,
    )