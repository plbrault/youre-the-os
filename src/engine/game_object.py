from abc import ABC, abstractmethod


class GameObject(ABC):
    # pylint: disable=too-few-public-methods

    @abstractmethod
    def update(self, current_time, events):
        pass
