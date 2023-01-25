import numpy as np

MAX_RANDOM_SEED_NUMBER = 4294967294


class Sampler:
    def __init__(self, seed: int = 123):
        self._seed = seed
        self._rng = np.random.RandomState(self._seed)

    def set_seed(self, seed=None, reseed=False):
        if seed:
            self._seed = seed
        elif reseed:
            self._seed = self._rng.randint(MAX_RANDOM_SEED_NUMBER)

        self._rng = np.random.RandomState(self._seed)

    def update(self, data):
        """[summary]

        Args:
            data ([type]): [description]
        """

    def reset(self):
        """[summary]

        Returns:
            [type]: [description]
        """
