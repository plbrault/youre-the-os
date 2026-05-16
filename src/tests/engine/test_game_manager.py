import pytest

from engine.game_manager import GameManager
from engine.modal import Modal
from engine.modal_view import ModalView
from engine.scene import Scene
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
        self.update_times = []
        super().__init__(StubModalView())

    def update(self, current_time, events):
        self.update_times.append(current_time)


class StubScene(Scene):
    def __init__(self):
        self.update_times = []
        self.update_events_list = []
        self.update_call_count = 0
        self._test_screen = None
        super().__init__('test')

    @property
    def screen(self):
        return self._test_screen

    def setup(self):
        self._scene_objects = []

    def update(self, current_time, events):
        self.update_times.append(current_time)
        self.update_events_list.append(events)
        self.update_call_count += 1


class TestGameManagerLocalTime:
    @pytest.fixture
    def game_manager(self):
        return GameManager()

    @pytest.fixture
    def scene(self, game_manager):
        import pygame
        scene = StubScene()
        scene._test_screen = pygame.Surface(WINDOW_SIZE)
        game_manager.register_scene(scene)
        game_manager._scene_manager.screen = scene._test_screen
        game_manager._scene_manager.start_scene(scene, 0)
        return scene

    def test_local_time_starts_at_zero_for_scene(self, game_manager, scene):
        game_manager._scene_manager.update(0, [])

        assert scene.update_times == [0]

    def test_local_time_advances_normally(self, game_manager, scene):
        game_manager._scene_manager.update(0, [])
        game_manager._scene_manager.update(1000, [])
        game_manager._scene_manager.update(2000, [])

        assert scene.update_times == [0, 1000, 2000]

    def test_local_time_freezes_when_modal_shown(self, game_manager, scene):
        game_manager._scene_manager.update(1000, [])

        modal = StubModal()
        scene.show_modal(modal)

        game_manager._scene_manager.update(5000, [])

        assert scene.update_times == [1000]
        assert modal.update_times == [4000]

    def test_local_time_resumes_after_modal_closed(self, game_manager, scene):
        game_manager._scene_manager.update(1000, [])

        modal = StubModal()
        scene.show_modal(modal)

        game_manager._scene_manager.update(5000, [])

        scene.close_modal()

        game_manager._scene_manager.update(6000, [])

        assert scene.update_times == [1000, 2000]
        assert modal.update_times == [4000]

    def test_local_time_pause_accumulates_across_multiple_pauses(self, game_manager, scene):
        game_manager._scene_manager.update(1000, [])

        modal1 = StubModal()
        scene.show_modal(modal1)

        game_manager._scene_manager.update(3000, [])

        scene.close_modal()

        game_manager._scene_manager.update(4000, [])

        modal2 = StubModal()
        scene.show_modal(modal2)

        game_manager._scene_manager.update(7000, [])

        scene.close_modal()

        game_manager._scene_manager.update(8000, [])

        assert scene.update_times == [1000, 2000, 3000]
        assert modal1.update_times == [2000]
        assert modal2.update_times == [3000]

    def test_modal_local_time_advances_normally(self, game_manager, scene):
        game_manager._scene_manager.update(1000, [])

        modal = StubModal()
        scene.show_modal(modal)

        game_manager._scene_manager.update(2000, [])
        game_manager._scene_manager.update(3000, [])
        game_manager._scene_manager.update(4000, [])

        assert scene.update_times == [1000]
        assert modal.update_times == [1000, 2000, 3000]

    def test_modal_local_time_resumes_correctly_after_multi_frame(self, game_manager, scene):
        game_manager._scene_manager.update(1000, [])

        modal = StubModal()
        scene.show_modal(modal)

        game_manager._scene_manager.update(2000, [])
        game_manager._scene_manager.update(3000, [])
        game_manager._scene_manager.update(4000, [])
        game_manager._scene_manager.update(5000, [])

        scene.close_modal()

        game_manager._scene_manager.update(6016, [])

        assert scene.update_times == [1000, 2016]
        assert modal.update_times == [1000, 2000, 3000, 4000]

    def test_scene_reset_resets_local_time(self, game_manager, scene):
        game_manager._scene_manager.update(1000, [])
        game_manager._scene_manager.update(5000, [])

        scene.reset()

        game_manager._scene_manager.update(6000, [])

        assert scene.update_times == [1000, 5000, 1000]
