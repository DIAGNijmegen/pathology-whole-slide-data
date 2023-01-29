from detectron2.engine import DefaultTrainer
from wholeslidedata.iterators import create_batch_iterator
from wholeslidedata.interoperability.detectron2.iterator import WholeSlideDetectron2Iterator

class WholeSlideDectectron2Trainer(DefaultTrainer):
    def __init__(self, cfg, user_config, cpus):

        self._user_config = user_config
        self._cpus = cpus

        super().__init__(cfg)

    def build_train_loader(self, cfg):
        mode = "training"

        training_batch_generator = create_batch_iterator(
            user_config=self._user_config,
            mode=mode,
            cpus=self._cpus,
            iterator_class=WholeSlideDetectron2Iterator,
        )
        return training_batch_generator