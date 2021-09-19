from concurrentbuffer.iterator import BufferIterator, buffer_iterator_factory

from wholeslidedata.buffer.batchcommander import BatchCommander
from wholeslidedata.buffer.batchproducer import BatchProducer
from wholeslidedata.buffer.utils import get_buffer_shape
from wholeslidedata.configuration.config import WholeSlideDataConfiguration


class BatchIterator(BufferIterator):
    def __init__(self, batch_size, index=0, stop_index=None, *args, **kwargs):
        self._batch_size = batch_size
        self._index = index
        self._stop_index = stop_index
        super().__init__(*args, **kwargs)

    @property
    def batch_size(self):
        return self._batch_size

    def __next__(self):
        if self._stop():
            raise StopIteration()
        return super().__next__()

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
    batches=None,
    presets=(),
    cpus=1,
    context="fork",
    determinstic=True,
):
    config_builder = WholeSlideDataConfiguration.build(
        user_config=user_config, modes=(mode,), build_instances=False, presets=presets
    )

    batch_commander = BatchCommander(
        config_builder=config_builder, mode=mode, reset_index=batches
    )

    batch_producer = BatchProducer(
        config_builder=config_builder, mode=mode, reset_index=batches
    )
    batch_size, buffer_shapes = get_buffer_shape(config_builder)

    return buffer_iterator_factory(
        batch_size=batch_size,
        stop_index=batches,
        cpus=cpus,
        buffer_shapes=buffer_shapes,
        commander=batch_commander,
        producer=batch_producer,
        context=context,
        deterministic=determinstic,
        buffer_iterator_class=BatchIterator,
    )
