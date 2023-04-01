from wholeslidedata.iterators.batchiterator import BatchIterator

class WholeSlidePlainnnUnetBatchIterator(BatchIterator):
    def __next__(self):
        x_batch, y_batch, _ = super().__next__()
        x_batch = x_batch.transpose(0,3,1,2).astype('float32')
        y_batch = y_batch.astype('int16')
        return {'data': x_batch, 'seg_all': y_batch}
