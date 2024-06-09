from abc import ABC, abstractmethod
import pygame

from ui.color import Color


class Scene(ABC):
    scene_manager = None
    screen: pygame.Surface
    background_color = Color.BLACK

    def __init__(self, scene_id: str):
        self._scene_id = scene_id
        self._is_started = False
        self._scene_objects = []

    @property
    def scene_id(self):
        return self._scene_id

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
