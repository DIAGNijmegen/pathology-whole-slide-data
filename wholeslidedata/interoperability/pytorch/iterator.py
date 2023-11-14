from wholeslidedata.iterators.batchiterator import BatchIterator

class WholeSlidePyTorchBatchIterator(BatchIterator):
    def __next__(self):
        x_batch, y_batch, *_ = super().__next__()
        x_batch = x_batch.transpose(0,3,1,2)
        return x_batch, y_batch
