import torch
from wholeslidedata.iterators.batchiterator import BatchIterator

# set dtype in create_batch_iterator to supported types e.g., int32, int16, int8, uint8


class TorchBatchIterator(BatchIterator):
    def __next__(self):
        if self._info_queue is not None:
            x_batch, y_batch, info = super().__next__()
            if len(x_batch.shape) == 5:
                x_batch = x_batch.transpose(1, 0, 4, 2, 3).astype("float32")
            else:
                x_batch = x_batch.transpose(0, 3, 1, 2).astype("float32")

            if len(x_batch.shape) == 5:
                y_batch = y_batch.transpose(1, 0, 4, 2, 3).astype("float32")
            elif len(x_batch.shape) == 4:
                y_batch = y_batch.transpose(0, 3, 1, 2).astype("float32")

            return (
                [torch.from_numpy(x).to(torch.device("cuda:0")) for x in x_batch],
                [torch.from_numpy(y).to(torch.device("cuda:0")) for y in y_batch],
                info,
            )
        raise ValueError("torch iterator works only with info")
