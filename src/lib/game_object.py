from abc import ABC, abstractmethod

class GameObject(ABC):
    def __init__(self, view):
        self._view = view

    @property
    def view(self):
        return self._view

    @abstractmethod
    def update(self, current_time, events):
        pass

    def render(self, surface):
        self._view.draw(surface)
