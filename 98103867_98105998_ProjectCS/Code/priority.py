from enum import Enum
from numpy.random import choice


class Priority(Enum):
    LOW = (1, 0.7)
    NORMAL = (2, 0.2)
    HIGH = (3, 0.1)

    @classmethod
    def get_priority_list(cls):
        return [cls.LOW, cls.NORMAL, cls.HIGH]

    @classmethod
    def get_priority_probabilities(cls):
        return [p.value[1] for p in cls.get_priority_list()]

    @classmethod
    def get_sample_priority(cls) -> "Priority":
        return choice(
            Priority.get_priority_list(), 1, p=Priority.get_priority_probabilities()
        )[0]
