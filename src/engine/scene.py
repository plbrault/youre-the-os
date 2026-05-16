from abc import abstractmethod
from typing import Optional
import pygame

from engine.game_object import GameObject
from engine.modal import Modal
from ui.color import Color


class Scene(GameObject):
    background_color = Color.BLACK

    def __init__(self, scene_id: str):
        super().__init__()
        self._scene_id = scene_id
        self._is_started = False
        self._scene_objects = []
        self._modal = None
        self._scene_manager = None

    @property
    def scene_manager(self):
        return self._scene_manager

    @scene_manager.setter
    def scene_manager(self, value):
        self._scene_manager = value

    @property
    def screen(self) -> pygame.Surface:
        return self.scene_manager.screen

    @property
    def scene_id(self):
        return self._scene_id

    @property
    def modal(self) -> Optional[Modal]:
        """Get the currently active modal, if any."""
        return self._modal

    @abstractmethod
    def setup(self):
        """Override to implement initialization of the scene.

        Do not call directly to reset the scene, use reset() instead.
        """

    def reset(self):
        """Reset the scene to its initial state.

        Performs any necessary cleanup, then calls setup() to reinitialize the scene.
        """
        self.close_modal()
        self.setup()
        if self.scene_manager is not None:
            self.scene_manager.reset_current_context_time()

    @abstractmethod
    def update(self, current_time, events):
        """Override to implement the update logic of the scene.

        Called every frame with the current time and a list of events.
        """

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
        if (
            self.scene_manager is not None
            and self.scene_manager.get_top_context() == self
        ):
            self.scene_manager.push_context(modal)

    def close_modal(self):
        """Close the currently active modal, if any."""
        if self._modal is None:
            return
        if self.scene_manager is not None:
            top_context = self.scene_manager.get_top_context()
            if top_context == self._modal:
                self.scene_manager.pop_context()
        modal = self._modal
        self._scene_objects.remove(modal)
        modal.scene = None
        self._modal = None

    def render(self):
        self.screen.fill(self.background_color)

        for scene_object in list(self._scene_objects):
            scene_object.render(self.screen)

        pygame.display.flip()
