from abc import ABC, abstractmethod


class GameObject(ABC):

    def __init__(self):
        self._children = []

    @property
    def children(self):
        return self._children

    @abstractmethod
    def update(self, current_time, player_inputs):
        pass
