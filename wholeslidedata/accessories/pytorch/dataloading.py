from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, datasets, models

class PytorchWholeSlideData(Dataset):
    def __init__(self, count, steps=None):
        self._steps = steps
        self.transform =  transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]) # imagenet
        ])

    def __len__(self):
        if self._steps is not None:
            return self._steps
        return super().__len__()

    def __getitem__(self, idx):
        image = self.input_images[idx]
        mask = self.target_masks[idx]
        if self.transform:
            image = self.transform(image)

        return [image, mask]


