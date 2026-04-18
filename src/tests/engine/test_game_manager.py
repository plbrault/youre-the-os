import pygame
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
        self._test_screen = pygame.Surface(WINDOW_SIZE)
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


class TestGameManagerTimeFreeze:
    @pytest.fixture
    def game_manager(self):
        return GameManager()

    @pytest.fixture
    def scene(self, game_manager):
        scene = StubScene()
        game_manager.register_scene(scene)
        game_manager.start_scene(scene)
        return scene

    def test_adjusted_time_passes_normally_without_modal(self, game_manager, scene, monkeypatch):
        monkeypatch.setattr('pygame.time.get_ticks', lambda: 1000)
        game_manager.step(scene, [])

        assert scene.update_times == [1000]

    def test_adjusted_time_freezes_when_modal_shown(self, game_manager, scene, monkeypatch):
        monkeypatch.setattr('pygame.time.get_ticks', lambda: 1000)
        game_manager.step(scene, [])

        modal = StubModal()
        scene.show_modal(modal)

        monkeypatch.setattr('pygame.time.get_ticks', lambda: 5000)
        game_manager.step(scene, [])

        assert scene.update_times == [1000]
        assert modal.update_times == [1000]

    def test_adjusted_time_resumes_after_modal_closed(self, game_manager, scene, monkeypatch):
        monkeypatch.setattr('pygame.time.get_ticks', lambda: 1000)
        game_manager.step(scene, [])

        modal = StubModal()
        scene.show_modal(modal)

        monkeypatch.setattr('pygame.time.get_ticks', lambda: 5000)
        game_manager.step(scene, [])

        scene.close_modal()

        monkeypatch.setattr('pygame.time.get_ticks', lambda: 6000)
        game_manager.step(scene, [])

        # Pause started at raw 5000 (first frame with modal), ended at raw 6000
        # Paused duration: 1000. Adjusted: 6000 - 1000 = 5000
        assert scene.update_times == [1000, 5000]
        assert modal.update_times == [1000]

    def test_adjusted_time_freeze_accumulates_across_multiple_pauses(self, game_manager, scene, monkeypatch):
        monkeypatch.setattr('pygame.time.get_ticks', lambda: 1000)
        game_manager.step(scene, [])

        modal1 = StubModal()
        scene.show_modal(modal1)

        monkeypatch.setattr('pygame.time.get_ticks', lambda: 3000)
        game_manager.step(scene, [])

        scene.close_modal()

        monkeypatch.setattr('pygame.time.get_ticks', lambda: 4000)
        game_manager.step(scene, [])

        modal2 = StubModal()
        scene.show_modal(modal2)

        monkeypatch.setattr('pygame.time.get_ticks', lambda: 7000)
        game_manager.step(scene, [])

        scene.close_modal()

        monkeypatch.setattr('pygame.time.get_ticks', lambda: 8000)
        game_manager.step(scene, [])

        # First pause: raw 3000 to raw 4000 = 1000
        # Second pause: raw 7000 to raw 8000 = 1000
        # Total paused: 2000. Adjusted: 8000 - 2000 = 6000
        assert scene.update_times == [1000, 3000, 6000]
        assert modal1.update_times == [1000]
        assert modal2.update_times == [3000]

    def test_frozen_time_stays_constant_across_multiple_frames(self, game_manager, scene, monkeypatch):
        monkeypatch.setattr('pygame.time.get_ticks', lambda: 1000)
        game_manager.step(scene, [])

        modal = StubModal()
        scene.show_modal(modal)

        monkeypatch.setattr('pygame.time.get_ticks', lambda: 2000)
        game_manager.step(scene, [])

        monkeypatch.setattr('pygame.time.get_ticks', lambda: 3000)
        game_manager.step(scene, [])

        monkeypatch.setattr('pygame.time.get_ticks', lambda: 4000)
        game_manager.step(scene, [])

        assert scene.update_times == [1000]
        assert modal.update_times == [1000, 1000, 1000]

    def test_adjusted_time_resumes_correctly_after_multi_frame_pause(self, game_manager, scene, monkeypatch):
        monkeypatch.setattr('pygame.time.get_ticks', lambda: 1000)
        game_manager.step(scene, [])

        modal = StubModal()
        scene.show_modal(modal)

        monkeypatch.setattr('pygame.time.get_ticks', lambda: 2000)
        game_manager.step(scene, [])

        monkeypatch.setattr('pygame.time.get_ticks', lambda: 3000)
        game_manager.step(scene, [])

        monkeypatch.setattr('pygame.time.get_ticks', lambda: 4000)
        game_manager.step(scene, [])

        monkeypatch.setattr('pygame.time.get_ticks', lambda: 5000)
        game_manager.step(scene, [])

        scene.close_modal()

        monkeypatch.setattr('pygame.time.get_ticks', lambda: 5016)
        game_manager.step(scene, [])

        # Pause started at raw 2000 (first frame with modal), ended at raw 5016
        # Paused duration: 3016. Adjusted: 5016 - 3016 = 2000
        assert scene.update_times == [1000, 2000]
        assert modal.update_times == [1000, 1000, 1000, 1000]