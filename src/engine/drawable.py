from abc import ABC, abstractmethod

import pygame


class Drawable(ABC):
    def __init__(self, x=0, y=0):
        self._x = x
        self._y = y
        self._target_x = None
        self._target_y = None

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

    @property
    def target_x(self):
        return self._target_x

    @target_x.setter
    def target_x(self, target_x):
        self._target_x = target_x

    @property
    def target_y(self):
        return self._target_y

    @target_y.setter
    def target_y(self, target_y):
        self._target_y = target_y

    def set_target_xy(self, target_x, target_y):
        self.target_x = target_x
        self.target_y = target_y

    def collides(self, x, y):
        return pygame.Rect(self._x, self._y, self.width,
                           self.height).collidepoint(x, y)

    def move_towards_target_xy(self, speed=None, *, x_speed=0, y_speed=0):
        if speed is not None:
            x_speed = speed
            y_speed = speed
        if self.target_x is not None:
            if self.x == self.target_x:
                self.target_x = None
            else:
                if self.x < self.target_x:
                    self.x += min(x_speed, self.target_x - self.x)
                if self.x > self.target_x:
                    self.x -= min(x_speed, self.x - self.target_x)
        if self.target_y is not None:
            if self.y == self.target_y:
                self.target_y = None
            else:
                if self.y < self.target_y:
                    self.y += min(y_speed, self.target_y - self.y)
                if self.y > self.target_y:
                    self.y -= min(y_speed, self.y - self.target_y)

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
