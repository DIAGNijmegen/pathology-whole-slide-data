import torch
from wholeslidedata.iterators.batchiterator import BatchIterator

# set dtype in create_batch_iterator to supported types e.g., int32, int16, int8, uint8

class TorchBatchIterator(BatchIterator):
    def __next__(self):
        if self._info_queue is not None:
            x_batch, y_batch, info = super().__next__()
            return torch.from_numpy(x_batch), torch.from_numpy(y_batch), info
        return map(torch.from_numpy, super().__next__())
