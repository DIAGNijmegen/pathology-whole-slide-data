from concurrentbuffer.iterator import BufferIterator, buffer_iterator_factory

from wholeslidedata.buffer.batchcommander import BatchCommander
from wholeslidedata.buffer.batchproducer import BatchProducer
from wholeslidedata.configuration.config import WholeSlideDataConfiguration


class BatchIterator(BufferIterator):
    def __init__(self, mode, batches=None, repeats=None, *args, **kwargs):
        self._modes = mode
        self._batches = batches
        self._repeats = repeats
        self._index = 0
        self._max_index = 0
        if not (self._batches is None or self._repeats is None):
            self._max_index = self._batches * self._repeats
        super().__init__(*args, **kwargs)

    def __next__(self):
        if self._max_index > 0 and self._index == self._max_index:
            self._index = 0
            raise StopIteration()
        batch = super().__next__()
        x_batch = batch[0][..., :3]
        y_batch = batch[1][..., 0]
        self._index += 1
        return x_batch, y_batch

    def __len__(self):
        if self._max_index == 0:
            raise TypeError('Batch iterator has no len() because it is infinite')
        return self._max_index


def create_batch_iterator(
    user_config,
    mode,
    cpus=1,
    batches=None,
    repeats=None,
    context="fork",
    determinstic=True,
):
    config_builder = WholeSlideDataConfiguration.build(
        user_config=user_config, modes=(mode,), build_instances=False
    )

    reset_index = None
    if batches is not None and repeats is not None:
        reset_index = batches

    batch_commander = BatchCommander(
        config_builder=config_builder, mode=mode, reset_index=reset_index
    )

    # x-batch.shape, y-batch.shape --> datapacker

    # create data packer -> batchproducer  and  to batch iterator
    # datapacker.shape
    shape = (2,) + tuple(
        [config_builder["training"]["batch_shape"]["batch_size"].cast()]
        + config_builder["training"]["batch_shape"]["shape"].cast()[:2]
        + [10]
    )

    batch_producer = BatchProducer(
        config_builder=config_builder, mode=mode, reset_index=reset_index
    )

    return buffer_iterator_factory(
        mode=mode,
        batches=batches,
        repeats=repeats,
        cpus=cpus,
        buffer_shape=shape,
        commander=batch_commander,
        producer=batch_producer,
        context=context,
        deterministic=determinstic,
        buffer_iterator_class=BatchIterator,
    )

