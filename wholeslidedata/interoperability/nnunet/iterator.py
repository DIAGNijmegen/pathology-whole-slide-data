from wholeslidedata.iterators.batchiterator import BatchIterator

class WholeSlidennUnetBatchIterator(BatchIterator):
    def __next__(self):
        x_batch, y_batch, _ = super().__next__()
        x_batch = x_batch.transpose(0,3,1,2).astype('float32')
        y_batch = y_batch.astype('int16')
        return {'data': x_batch, 'target': y_batch}
