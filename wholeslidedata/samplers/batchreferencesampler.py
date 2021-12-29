class BatchReferenceSampler:
    def __init__(
        self, dataset, batch_size, label_sampler, annotation_sampler, point_sampler
    ):

        self._dataset = dataset
        self._batch_size = batch_size
        self._label_sampler = label_sampler
        self._annotation_sampler = annotation_sampler
        self._point_sampler = point_sampler

    @property
    def dataset(self):
        return self._dataset

    @property
    def mode(self):
        return self._dataset.mode

    def reset(self):
        self._label_sampler.reset()
        self._annotation_sampler.reset()
        self._point_sampler.reset()

    def update(self, batch):
        self._label_sampler.update(batch)
        self._annotation_sampler.update(batch)

    def batch(self):
        batch = []
        for _ in range(self._batch_size):
            # get next label
            label = next(self._label_sampler)

            # get next index of label
            index = next(self._annotation_sampler)(label)

            # get new sample to samples
            sample = self._dataset.sample_references[label][index]

            point = self._point_sampler.sample(sample)

            # add new sample to samples
            batch.append({'reference': sample, 'point': point})

        return batch
