import torch
from detectron2.structures import Boxes, Instances
from wholeslidedata.iterators import BatchIterator
import numpy as np

class WholeSlideDetectron2Iterator(BatchIterator):
    MIN_DETECTION_SIZE = 4

    def __next__(self):
        x_batch, y_batch, _ = super().__next__()
        batch_dicts = []
        for idx, image in enumerate(x_batch):
            sample_dict = {}
            target_gt_boxes = self._get_gt_boxes(y_batch[idx], image.shape[:2])
            image = image.transpose(2, 0, 1).astype("float32")
            sample_dict["instances"] = target_gt_boxes
            sample_dict["image"] = torch.as_tensor(image)
            batch_dicts.append(sample_dict)
        return batch_dicts

    def _get_gt_boxes(self, y_sample, image_size):
        y_boxes = y_sample[~np.all(y_sample == 0, axis=-1)]
        boxes = y_boxes[..., :4].astype("int32")
        target_boxes = []
        target_classes = []
        for idx, box in enumerate(boxes):

            if (box[2] - box[0]) < WholeSlideDetectron2Iterator.MIN_DETECTION_SIZE:
                continue
            if (box[3] - box[1]) < WholeSlideDetectron2Iterator.MIN_DETECTION_SIZE:
                continue

            target_boxes.append(box)
            target_classes.append(y_boxes[idx][-2] - 1)

        target = Instances(image_size)
        target_boxes = np.array(target_boxes)
        target.gt_boxes = Boxes(target_boxes)
        classes = torch.tensor(target_classes, dtype=torch.int64)
        target.gt_classes = classes
        return target
