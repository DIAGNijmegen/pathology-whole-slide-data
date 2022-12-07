from enum import Enum, auto


class WholeSlideMode(Enum):
    default = auto()
    training = auto()
    validation = auto()
    test = auto()
    inference = auto()


create_mode = lambda name: WholeSlideMode[name]