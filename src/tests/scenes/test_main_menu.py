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
        menu.scene_manager = scene_manager
        menu.setup()
        scene_manager._current_scene = menu
        scene_manager._scenes['main_menu'] = menu
        return menu

    def test_scene_transition_closes_active_modal(self, main_menu, scene_manager):
        main_menu.show_modal(StubModal())

        scene_manager.start_scene('main_menu')

        assert main_menu.modal is None

    def test_update_routes_to_scene_objects_after_modal_transition(self, main_menu, scene_manager):
        main_menu.show_modal(StubModal())

        scene_manager.start_scene('main_menu')

        update_received = False
        for scene_object in main_menu._scene_objects:
            original_update = scene_object.update

            def make_spy(orig):
                def spy(current_time, events):
                    nonlocal update_received
                    update_received = True
                    orig(current_time, events)
                return spy

            scene_object.update = make_spy(original_update)

        main_menu.update(0, [])

        assert update_received
