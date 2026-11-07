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
        self._modals = []
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
    def active_modal(self) -> Optional[Modal]:
        """Get the active modal, if any."""
        return self._modals[-1] if self._modals else None

    @abstractmethod
    def setup(self):
        """Override to implement initialization of the scene.

        Do not call directly to reset the scene, use reset() instead.
        """

    def reset(self):
        """Reset the scene to its initial state.

        Performs any necessary cleanup, then calls setup() to reinitialize the scene.
        """
        while self._modals:
            self.close_modal()
        self.setup()
        if self.scene_manager is not None:
            self.scene_manager.reset_current_context_time()

    @abstractmethod
    def update(self, current_time, player_inputs):
        """Override to implement the update logic of the scene.

        Called every frame with the current time and a list of player inputs.
        """

    def open_modal(self, modal : Modal):
        """Open a modal on the scene. It becomes the active modal; a previously
        active modal, if any, stays underneath."""
        top_modal = self.active_modal
        modal.scene = self
        modal.view.set_xy(
            (self.screen.get_width() - modal.view.width) / 2,
            (self.screen.get_height() - modal.view.height) / 2
        )
        self._children.append(modal)
        self._modals.append(modal)
        if self.scene_manager is not None:
            top_context = self.scene_manager.get_top_context()
            if top_context is self or (
                top_modal is not None and top_context is top_modal
            ):
                self.scene_manager.push_context(modal)

    def close_modal(self):
        """Close the active modal, if any."""
        if not self._modals:
            return
        modal = self._modals[-1]
        if self.scene_manager is not None:
            top_context = self.scene_manager.get_top_context()
            if top_context == modal:
                self.scene_manager.pop_context()
        self._children.remove(modal)
        modal.scene = None
        self._modals.pop()

    def render(self):
        self.screen.fill(self.background_color)

        for scene_object in list(self._children):
            scene_object.render(self.screen)

        pygame.display.flip()
