import torch
from wholeslidedata.iterators.batchiterator import BatchIterator

# set dtype in create_batch_iterator to supported types e.g., int32, int16, int8, uint8
class TorchBatchIterator(BatchIterator):
    def __next__(self):
        x_batch, y_batch, info = super().__next__()
        x_batch = x_batch / 255.0
        x_batch = x_batch.transpose(1, 0, 4, 2, 3).astype("float32")
        y_batch = y_batch.transpose(1, 0, 4, 2, 3).astype("float32")
        return (
            [torch.from_numpy(x).cuda() for x in x_batch],
            [torch.from_numpy(y).cuda() for y in y_batch],
            info,
        )
