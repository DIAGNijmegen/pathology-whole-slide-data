import cv2
import torch
from detectron2.engine import DefaultPredictor


class BatchPredictor(DefaultPredictor):

    def __call__(self, images):
        input_images = []
        for image in images:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            image = image.astype("float32")
            image = image[:, :, ::-1]
            if self.input_format == "RGB":
                image = image[:, :, ::-1]
            height, width = image.shape[:2]
            image = self.aug.get_transform(image).apply_image(image)
            image = torch.as_tensor(image.astype("float32").transpose(2, 0, 1))
            input_images.append({"image": image, "height": height, "width": width})

        with torch.no_grad():
            preds = self.model(input_images)
        return preds


class Detectron2DetectionPredictor:
    def __init__(self, cfg):
        self._predictor = BatchPredictor(cfg)

    def predict_on_batch(self, x_batch):
        # format is documented at https://detectron2.readthedocs.io/tutorials/models.html#model-output-format
        outputs = self._predictor(x_batch)
        predictions = []
        for output in outputs:
            pred_boxes = output["instances"].get("pred_boxes")
            scores = output["instances"].get("scores")
            classes = output["instances"].get("pred_classes")
            record = {}
            record["boxes"] = []
            record["confidences"] = []
            record["classes"] = []
            for idx, pred_box in enumerate(pred_boxes):
                record["boxes"].append(list(pred_box.cpu().detach().numpy()) + [1, 1])
                record["confidences"].append(scores[idx].cpu().detach().numpy())
                record["classes"].append(classes[idx].cpu().detach().numpy())
            predictions.append(record)
        return predictions