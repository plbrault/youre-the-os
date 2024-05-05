from abc import ABC, abstractmethod

import pygame

from engine.scene_manager import SceneManager
from ui.color import Color


class Scene(ABC):
    scene_manager: SceneManager
    screen: pygame.Surface
    scenes: dict
    background_color = Color.BLACK

    def __init__(self, name):
        self._name = name
        self._is_started = False
        self._scene_objects = []

    def start(self):
        self.scene_manager.start_scene(self)

    @property
    def name(self):
        return self._name

    @property
    def current_time(self):
        return pygame.time.get_ticks()

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def update(self, current_time, events):
        pass

    def render(self):
        self.screen.fill(self.background_color)

        for game_object in self._scene_objects:
            game_object.render(self.screen)

        pygame.display.flip()
