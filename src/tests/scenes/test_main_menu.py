import pygame
import pytest

from engine.modal import Modal
from engine.modal_view import ModalView
from engine.scene_manager import SceneManager
from scenes.main_menu import MainMenu
from window_size import WINDOW_SIZE


class StubModalView(ModalView):
    def __init__(self):
        super().__init__()

    @property
    def width(self):
        return 200

    @property
    def height(self):
        return 100

    def draw_content(self, surface):
        pass


class StubModal(Modal):
    def __init__(self):
        super().__init__(StubModalView())


class TestMainMenuSceneTransition:
    @pytest.fixture
    def scene_manager(self):
        sm = SceneManager()
        sm.screen = pygame.Surface(WINDOW_SIZE)
        return sm

    @pytest.fixture
    def main_menu(self, scene_manager):
        menu = MainMenu()
        scene_manager.register_scene(menu)
        scene_manager.start_scene(menu)
        return menu

    def test_scene_transition_closes_active_modal(self, main_menu, scene_manager):
        main_menu.show_modal(StubModal())

        scene_manager.start_scene('main_menu')

        assert main_menu.modal is None