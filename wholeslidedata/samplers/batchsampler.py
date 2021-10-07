from typing import List
from wholeslidedata.dataset import WholeSlideDataSet, WholeSlideSampleReference
from wholeslidedata.samplers.structures import Batch


class BatchSampler:
    def __init__(self, dataset: WholeSlideDataSet, sampler, batch_callbacks=None):
        self._dataset = dataset
        self._sampler = sampler
        self._batch_callbacks = batch_callbacks

    @property
    def dataset(self):
        return self._dataset

    def batch(self, batch_data: List[WholeSlideSampleReference], i=None):
        batch_data = self._sample_batch(batch_data, i)
        batch_data = self._apply_batch_callbacks(batch_data)
        return batch_data

    def _sample_batch(self, batch_data: List[WholeSlideSampleReference], i):
        # decalare x_batch and y_batch
        x_batch = []
        y_batch = []
        for sample_reference in batch_data:
            wsi = self._dataset.get_image_from_reference(sample_reference['reference'])
            wsa = self._dataset.get_wsa_from_reference(sample_reference['reference'])
            point = sample_reference['point']
            x_samples, y_samples = self._sampler.sample(wsi, wsa, point)

            # append samples to batch
            x_batch.append(x_samples)
            y_batch.append(y_samples)

        return x_batch, y_batch

    def _apply_batch_callbacks(self, batch_data):
        if self._batch_callbacks:
            for callback in self._batch_callbacks:
                if isinstance(batch_data, tuple):
                    batch_data = callback(*batch_data)
                elif isinstance(batch_data, dict):
                    batch_data = callback(**batch_data)
        return batch_data

    def reset(self):
        self._sampler.reset()
