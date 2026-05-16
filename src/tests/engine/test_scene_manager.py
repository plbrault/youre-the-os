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


class TestSceneManagerUpdateBehavior:
    @pytest.fixture
    def scene_manager(self):
        return SceneManager()

    def test_modal_push_during_update_does_not_cause_duplicate_update(self, scene_manager):
        """When a modal is pushed during scene update, no duplicate update should occur in the same frame."""
        scene = StubGameObject()
        modal = StubGameObject()

        scene_manager.start_scene(scene, 0)

        scene_manager.update(0, [])
        assert scene.update_times == [0]
        assert modal.update_times == []

        def scene_update_with_push(current_time, events):
            scene.update_times.append(current_time)
            scene.update_events_list.append(events)
            # Only push once
            if not modal.update_times:
                scene_manager.push_context(modal)

        original_update = scene.update
        scene.update = scene_update_with_push

        scene_manager.update(1000, ['event1'])

        scene.update = original_update

        # Pushing a modal during update should not cause an extra update in the same frame
        assert modal.update_times == []

        # The modal should be updated starting from the next frame
        scene_manager.update(2000, [])
        assert modal.update_times == [1000]

    def test_modal_pop_during_update_does_not_cause_duplicate_update(self, scene_manager):
        """When a modal is popped during modal update, no duplicate update should occur in the same frame."""
        scene = StubGameObject()
        modal = StubGameObject()

        scene_manager.start_scene(scene, 0)
        scene_manager.push_context(modal)

        scene_manager.update(1000, [])
        assert scene.update_times == []
        assert modal.update_times == [1000]

        def modal_update_with_pop(current_time, events):
            modal.update_times.append(current_time)
            modal.update_events_list.append(events)
            scene_manager.pop_context()

        original_modal_update = modal.update
        modal.update = modal_update_with_pop

        scene_manager.update(2000, ['event1'])

        modal.update = original_modal_update

        # Popping a modal during update should not cause the scene to be updated in the same frame
        assert modal.update_times == [1000, 2000]
        assert scene.update_times == []

        # The scene should be updated starting from the next frame
        scene_manager.update(3000, [])
        assert scene.update_times == [1000]

    def test_scene_switch_during_update_triggers_second_update(self, scene_manager):
        """When start_scene is called during update, the new scene should get a second update with empty events."""
        scene1 = StubGameObject()
        scene2 = StubGameObject()

        scene_manager.start_scene(scene1, 0)

        scene_manager.update(0, [])
        assert scene1.update_times == [0]
        assert scene2.update_times == []

        def scene1_update_with_switch(current_time, events):
            scene1.update_times.append(current_time)
            scene1.update_events_list.append(events)
            scene_manager.start_scene(scene2, None)

        original_update = scene1.update
        scene1.update = scene1_update_with_switch

        scene_manager.update(1000, ['event1', 'event2'])

        scene1.update = original_update

        # scene1 was updated with the original events
        assert scene1.update_times == [0, 1000]
        assert scene1.update_events_list == [[], ['event1', 'event2']]

        # scene2 was updated with empty events after the scene switch
        assert scene2.update_times == [0]
        assert scene2.update_events_list == [[]]
