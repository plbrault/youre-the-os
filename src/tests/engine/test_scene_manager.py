import pytest

from engine.game_object import GameObject
from engine.scene_manager import SceneManager


class StubGameObject(GameObject):
    """Stub GameObject for testing SceneManager."""

    def __init__(self):
        super().__init__()
        self.update_times = []
        self.update_events_list = []
        self.reset_call_count = 0

    def update(self, current_time, events):
        self.update_times.append(current_time)
        self.update_events_list.append(events)

    def reset(self):
        """Reset stub for testing scene switching."""
        self.reset_call_count += 1
        self.update_times = []
        self.update_events_list = []


class TestSceneManagerLocalTime:
    @pytest.fixture
    def scene_manager(self):
        return SceneManager()

    @pytest.fixture
    def scene(self):
        return StubGameObject()

    @pytest.fixture
    def modal(self):
        return StubGameObject()

    def test_local_time_starts_at_zero_for_scene(self, scene_manager, scene):
        scene_manager.start_scene(scene, 0)
        scene_manager.update(0, [])

        assert scene.update_times == [0]

    def test_local_time_advances_normally(self, scene_manager, scene):
        scene_manager.start_scene(scene, 0)
        scene_manager.update(0, [])
        scene_manager.update(1000, [])
        scene_manager.update(2000, [])

        assert scene.update_times == [0, 1000, 2000]

    def test_local_time_freezes_when_modal_shown(self, scene_manager, scene, modal):
        scene_manager.start_scene(scene, 0)
        scene_manager.update(1000, [])

        scene_manager.push_context(modal)
        scene_manager.update(5000, [])

        assert scene.update_times == [1000]
        assert modal.update_times == [4000]

    def test_local_time_resumes_after_modal_closed(self, scene_manager, scene, modal):
        scene_manager.start_scene(scene, 0)
        scene_manager.update(1000, [])

        scene_manager.push_context(modal)
        scene_manager.update(5000, [])

        scene_manager.pop_context()
        scene_manager.update(6000, [])

        assert scene.update_times == [1000, 2000]
        assert modal.update_times == [4000]

    def test_local_time_pause_accumulates_across_multiple_pauses(self, scene_manager, scene):
        modal1 = StubGameObject()
        modal2 = StubGameObject()

        scene_manager.start_scene(scene, 0)
        scene_manager.update(1000, [])

        scene_manager.push_context(modal1)
        scene_manager.update(3000, [])

        scene_manager.pop_context()
        scene_manager.update(4000, [])

        scene_manager.push_context(modal2)
        scene_manager.update(7000, [])

        scene_manager.pop_context()
        scene_manager.update(8000, [])

        assert scene.update_times == [1000, 2000, 3000]
        assert modal1.update_times == [2000]
        assert modal2.update_times == [3000]

    def test_modal_local_time_advances_normally(self, scene_manager, scene, modal):
        scene_manager.start_scene(scene, 0)
        scene_manager.update(1000, [])

        scene_manager.push_context(modal)
        scene_manager.update(2000, [])
        scene_manager.update(3000, [])
        scene_manager.update(4000, [])

        assert scene.update_times == [1000]
        assert modal.update_times == [1000, 2000, 3000]

    def test_modal_local_time_resumes_correctly_after_multi_frame(self, scene_manager, scene, modal):
        scene_manager.start_scene(scene, 0)
        scene_manager.update(1000, [])

        scene_manager.push_context(modal)
        scene_manager.update(2000, [])
        scene_manager.update(3000, [])
        scene_manager.update(4000, [])
        scene_manager.update(5000, [])

        scene_manager.pop_context()
        scene_manager.update(6016, [])

        assert scene.update_times == [1000, 2016]
        assert modal.update_times == [1000, 2000, 3000, 4000]

    def test_scene_reset_resets_local_time(self, scene_manager, scene):
        scene_manager.start_scene(scene, 0)
        scene_manager.update(1000, [])
        scene_manager.update(5000, [])

        scene_manager.reset_current_context_time()
        scene_manager.update(6000, [])

        assert scene.update_times == [1000, 5000, 1000]

    def test_get_top_context_returns_top_context(self, scene_manager, scene, modal):
        scene_manager.start_scene(scene, 0)
        assert scene_manager.get_top_context() is scene

        scene_manager.push_context(modal)
        assert scene_manager.get_top_context() is modal

    def test_get_top_context_returns_none_when_empty(self, scene_manager):
        assert scene_manager.get_top_context() is None

    def test_pop_context_prevents_popping_root_context(self, scene_manager, scene):
        scene_manager.start_scene(scene, 0)

        # Should not pop the root scene
        result = scene_manager.pop_context()
        assert result is None
        assert scene_manager.get_top_context() is scene

    def test_update_with_empty_stack_does_not_crash(self, scene_manager):
        scene_manager.update(1000, [])
        # Should not raise an exception
