from abc import ABC, abstractmethod

import pygame


class Drawable(ABC):
    def __init__(self, x=0, y=0):
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x):
        self._x = x

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        self._y = y

    def set_xy(self, x, y):
        self.x = x
        self.y = y

    def collides(self, x, y):
        return pygame.Rect(self._x, self._y, self.width,
                           self.height).collidepoint(x, y)

    @property
    @abstractmethod
    def width(self):
        pass

    @property
    @abstractmethod
    def height(self):
        pass

    @abstractmethod
    def draw(self, surface):
        pass
