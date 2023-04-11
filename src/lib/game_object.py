from abc import ABC, abstractmethod

class GameObject(ABC):
    def __init__(self, view):
        self._view = view
        self._children = []

    @property
    def view(self):
        return self._view
    
    @property
    def children(self):
        return self._children

    def update(self, current_time, events):
        for child in self._children:
            child.update(current_time, events)

    def render(self, surface):
        self._view.draw(surface)
        for child in self._children:
            child.render(surface)
