from abc import ABC, abstractmethod
import pygame

from engine.modal import Modal
from ui.color import Color


class Scene(ABC):
    scene_manager = None
    background_color = Color.BLACK

    def __init__(self, scene_id: str):
        self._scene_id = scene_id
        self._is_started = False
        self._scene_objects = []
        self._modal = None
        self._current_time = 0

    @property
    def screen(self) -> pygame.Surface:
        return self.scene_manager.screen

    @property
    def scene_id(self):
        return self._scene_id

    @property
    def current_time(self):
        return self._current_time

    @current_time.setter
    def current_time(self, value):
        self._current_time = value

    @property
    def modal(self) -> Modal:
        """Get the currently active modal, if any."""
        return self._modal

    @abstractmethod
    def setup(self):
        """Override this method to implement initialization of the scene. Do not call directly to reset the scene, use `reset()` instead."""
        pass

    def reset(self):
        """Reset the scene to its initial state. This will perform any necessary cleanup and then call `setup()` to reinitialize the scene."""
        self.close_modal()
        self.setup()

    @abstractmethod
    def update(self, current_time, events):
        """Override this method to implement the update logic of the scene. This method will be called every frame with the current time and a list of events."""
        pass

    def show_modal(self, modal : Modal):
        """Show a modal on top of the scene. Only one modal can be active at a time."""
        if self._modal is not None:
            raise RuntimeError('A modal is already active.')
        modal.scene = self
        modal.view.set_xy(
            (self.screen.get_width() - modal.view.width) / 2,
            (self.screen.get_height() - modal.view.height) / 2
        )
        self._scene_objects.append(modal)
        self._modal = modal
        modal.on_open()

    def close_modal(self):
        """Close the currently active modal, if any."""
        if self._modal is None:
            return
        self._scene_objects.remove(self._modal)
        modal = self._modal
        self._modal = None
        modal.on_close()

    def render(self):
        self.screen.fill(self.background_color)

        for scene_object in self._scene_objects:
            scene_object.render(self.screen)

        pygame.display.flip()
