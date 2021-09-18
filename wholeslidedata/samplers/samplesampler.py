from typing import List

from wholeslidedata.annotation.structures import Annotation
from wholeslidedata.annotation.wholeslideannotation import WholeSlideAnnotation
from wholeslidedata.image.wholeslideimage import WholeSlideImage
from wholeslidedata.samplers.patchlabelsampler import PatchLabelSampler
from wholeslidedata.samplers.patchsampler import PatchSampler
from wholeslidedata.samplers.pointsampler import PointSampler
from wholeslidedata.samplers.structures import BatchShape, Sample


class SampleSampler:
    def __init__(
        self,
        point_sampler: PointSampler,
        patch_sampler: PatchSampler,
        patch_label_sampler: PatchLabelSampler,
        batch_shape: BatchShape,
        sample_callbacks=None,
    ):
        self._batch_shape = batch_shape
        self._point_sampler = point_sampler
        self._patch_sampler = patch_sampler
        self._patch_label_sampler = patch_label_sampler
        self._sample_callbacks = sample_callbacks

    def sample(self, wsi: WholeSlideImage, wsa: WholeSlideAnnotation, annotation: Annotation):
        x_samples = self._init_samples()
        y_samples = self._init_samples()

        point = self._point_sampler.sample(
            annotation,
            list(self._batch_shape.values())[0][-1][0],
            list(self._batch_shape.values())[0][-1][1],
            wsi.get_downsampling_from_spacing(list(self._batch_shape.keys())[-1]),
        )

        for pixel_spacing, shapes in self._batch_shape.items():
            for patch_shape in shapes:

                x_sample, y_sample = self._sample(
                    point, wsi, wsa, annotation, patch_shape, pixel_spacing
                )

                x_samples[pixel_spacing][tuple(patch_shape)] = x_sample

                y_samples[pixel_spacing][tuple(patch_shape)] = y_sample

        self._reset_sample_callbacks()
        return x_samples, y_samples

    def _sample(
        self,
        point: tuple,
        wsi: WholeSlideImage,
        wsa: WholeSlideAnnotation,
        annotation: Annotation,
        patch_shape,
        pixel_spacing: float,
    ):

        patch = self._patch_sampler.sample(wsi, point, patch_shape[:2], pixel_spacing)

        ratio = wsi.get_downsampling_from_spacing(pixel_spacing)
        label = self._patch_label_sampler.sample(
            wsa=wsa,
            point=point,
            size=patch_shape[:2],
            ratio=ratio,
        )

        patch, label = self._apply_sample_callbacks(patch, label)

        x_sample = self._create_sample(
            patch,
            wsi.path,
            annotation.label.name,
            annotation.index,
            point,
            wsi.get_real_spacing(pixel_spacing),
        )
        y_sample = self._create_sample(
            label,
            wsi.path,
            annotation.label.name,
            annotation.index,
            point,
            wsi.get_real_spacing(pixel_spacing),
        )

        return x_sample, y_sample

    def _init_samples(self):
        return {
            spacing: {tuple(input_size): [] for input_size in sizes}
            for spacing, sizes in self._batch_shape.items()
        }

    def _create_sample(
        self, sample_data, image_path, label_name, index, point, pixel_spacing
    ):
        return Sample(
            sample_data,
            image_path,
            label_name,
            index,
            point,
            pixel_spacing,
        )

    def _reset_sample_callbacks(self):
        if self._sample_callbacks:
            for callback in self._sample_callbacks:
                callback.reset()

    def _apply_sample_callbacks(self, patch, mask):
        if self._sample_callbacks:
            for callback in self._sample_callbacks:
                patch, mask = callback(patch, mask)

        return patch, mask

    def reset(self):
        self._point_sampler.reset()
