from abc import ABC

from engine.drawable import Drawable


class GameObject(ABC):
    def __init__(self, view: Drawable):
        self._view = view
        self._visible = True
        self._children = []

    @property
    def view(self):
        return self._view

    @property
    def children(self):
        return self._children

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value: bool):
        self._visible = value

    def update(self, current_time, events):
        for child in self._children:
            child.update(current_time, events)

    def render(self, surface):
        if self.visible:
            self._view.draw(surface)
            for child in self._children:
                child.render(surface)
