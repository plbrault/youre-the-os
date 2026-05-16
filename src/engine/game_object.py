from abc import ABC, abstractmethod


class GameObject(ABC):
    @abstractmethod
    def update(self, current_time, events):
        pass
