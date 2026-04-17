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
        super().__init__(StubModalView())


class StubScene(Scene):
    def __init__(self):
        self.last_update_time = None
        self.last_update_events = None
        self.update_call_count = 0
        super().__init__('test')

    def setup(self):
        self._scene_objects = []

    def update(self, current_time, events):
        self.last_update_time = current_time
        self.last_update_events = events
        self.update_call_count += 1


class TestGameManagerTimeFreeze:
    @pytest.fixture
    def game_manager(self):
        gm = GameManager()
        gm._screen = pygame.Surface(WINDOW_SIZE)
        gm._scene_manager.screen = gm._screen
        return gm

    @pytest.fixture
    def scene(self):
        scene = StubScene()
        scene.scene_manager = type('FakeSceneManager', (), {
            'screen': pygame.Surface(WINDOW_SIZE)
        })()
        scene.setup()
        return scene

    def _tick(self, game_manager, scene, monkeypatch, ticks):
        monkeypatch.setattr('pygame.time.get_ticks', lambda: ticks)
        adjusted = game_manager._get_adjusted_time(scene)
        scene.current_time = adjusted
        return adjusted

    def test_adjusted_time_passes_normally_without_modal(self, game_manager, scene, monkeypatch):
        adjusted = self._tick(game_manager, scene, monkeypatch, 1000)

        assert adjusted == 1000

    def test_adjusted_time_freezes_when_modal_shown(self, game_manager, scene, monkeypatch):
        self._tick(game_manager, scene, monkeypatch, 1000)

        scene.show_modal(StubModal())

        adjusted = self._tick(game_manager, scene, monkeypatch, 5000)

        assert adjusted == 1000

    def test_adjusted_time_resumes_after_modal_closed(self, game_manager, scene, monkeypatch):
        self._tick(game_manager, scene, monkeypatch, 1000)

        scene.show_modal(StubModal())
        self._tick(game_manager, scene, monkeypatch, 5000)

        scene.close_modal()

        adjusted = self._tick(game_manager, scene, monkeypatch, 6000)

        # Pause started at raw 5000 (first frame with modal), ended at raw 6000
        # Paused duration: 1000. Adjusted: 6000 - 1000 = 5000
        assert adjusted == 5000

    def test_adjusted_time_freeze_accumulates_across_multiple_pauses(self, game_manager, scene, monkeypatch):
        self._tick(game_manager, scene, monkeypatch, 1000)

        modal1 = StubModal()
        scene.show_modal(modal1)
        self._tick(game_manager, scene, monkeypatch, 3000)

        scene.close_modal()
        self._tick(game_manager, scene, monkeypatch, 4000)

        modal2 = StubModal()
        scene.show_modal(modal2)
        self._tick(game_manager, scene, monkeypatch, 7000)

        scene.close_modal()

        adjusted = self._tick(game_manager, scene, monkeypatch, 8000)

        # First pause: raw 3000 to raw 4000 = 1000
        # Second pause: raw 7000 to raw 8000 = 1000
        # Total paused: 2000. Adjusted: 8000 - 2000 = 6000
        assert adjusted == 6000

    def test_scene_current_time_set_to_adjusted_time(self, game_manager, scene, monkeypatch):
        self._tick(game_manager, scene, monkeypatch, 5000)

        assert scene.current_time == 5000

    def test_frozen_time_stays_constant_across_multiple_frames(self, game_manager, scene, monkeypatch):
        self._tick(game_manager, scene, monkeypatch, 1000)

        scene.show_modal(StubModal())

        assert self._tick(game_manager, scene, monkeypatch, 2000) == 1000
        assert self._tick(game_manager, scene, monkeypatch, 3000) == 1000
        assert self._tick(game_manager, scene, monkeypatch, 4000) == 1000

    def test_adjusted_time_resumes_correctly_after_multi_frame_pause(self, game_manager, scene, monkeypatch):
        self._tick(game_manager, scene, monkeypatch, 1000)

        scene.show_modal(StubModal())

        self._tick(game_manager, scene, monkeypatch, 2000)
        self._tick(game_manager, scene, monkeypatch, 3000)
        self._tick(game_manager, scene, monkeypatch, 4000)
        self._tick(game_manager, scene, monkeypatch, 5000)

        scene.close_modal()

        adjusted = self._tick(game_manager, scene, monkeypatch, 5016)

        # Pause started at raw 2000 (first frame with modal), ended at raw 5016
        # Paused duration: 3016. Adjusted: 5016 - 3016 = 2000
        assert adjusted == 2000
