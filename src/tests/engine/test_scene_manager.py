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
        """When a modal is pushed during scene update, the modal should only be updated once."""
        scene = StubGameObject()
        modal = StubGameObject()

        scene_manager.start_scene(scene, 0)

        # First update at t=0 to establish baseline
        scene_manager.update(0, [])
        assert scene.update_times == [0]
        assert modal.update_times == []

        # Second update where scene pushes modal
        def scene_update_with_push(current_time, events):
            scene.update_times.append(current_time)
            scene.update_events_list.append(events)
            if not modal.update_times:  # Only push once
                scene_manager.push_context(modal)

        # Replace scene's update method
        original_update = scene.update
        scene.update = scene_update_with_push

        scene_manager.update(1000, ['event1'])

        # Restore original update
        scene.update = original_update

        # Scene should have been updated twice (once by us, once by SceneManager)
        # Actually the scene_update_with_push appends, then SceneManager checks for scene change
        # Since scene didn't change, no second update
        # Modal should have been pushed but NOT updated in this frame
        # Wait, let me reconsider...

        # When scene.update is called, it pushes the modal
        # After scene.update returns, SceneManager checks if _current_scene changed
        # It hasn't (only modal was pushed), so no second update
        # Modal was pushed but won't be updated until next frame

        # Actually I need to verify the actual behavior
        # Let me check what happens:
        # 1. update(1000, ['event1']) is called
        # 2. local_time = 1000 - 0 - 0 = 1000
        # 3. active_context = scene
        # 4. scene.update(1000, ['event1']) is called
        # 5. Inside scene.update, we push modal to context stack
        # 6. After scene.update returns, check if _current_scene changed - it hasn't
        # 7. No second update triggered
        # 8. Next call to update will update modal

        # So modal.update_times should be empty after first update
        assert modal.update_times == []

        # Next frame should update modal
        scene_manager.update(2000, [])
        assert modal.update_times == [1000]  # 2000 - 1000 (start_time) - 0 = 1000

    def test_modal_pop_during_update_does_not_cause_duplicate_update(self, scene_manager):
        """When a modal is popped during modal update, the scene should only be updated once."""
        scene = StubGameObject()
        modal = StubGameObject()

        scene_manager.start_scene(scene, 0)
        scene_manager.push_context(modal)

        # Update to establish baseline
        scene_manager.update(1000, [])
        assert scene.update_times == []
        assert modal.update_times == [1000]

        # Update where modal pops itself
        def modal_update_with_pop(current_time, events):
            modal.update_times.append(current_time)
            modal.update_events_list.append(events)
            scene_manager.pop_context()

        original_modal_update = modal.update
        modal.update = modal_update_with_pop

        scene_manager.update(2000, ['event1'])

        modal.update = original_modal_update

        # Modal was updated once, popped the context
        # Scene was not updated in this frame because modal was active context
        # After modal.update, check if _current_scene changed - it hasn't
        assert modal.update_times == [1000, 2000]
        assert scene.update_times == []  # Scene still paused

        # Next frame should update scene
        scene_manager.update(3000, [])
        # Scene start_time is 0, paused_time is 2000 (duration modal was active)
        # local_time = 3000 - 0 - 2000 = 1000
        assert scene.update_times == [1000]

    def test_scene_switch_during_update_triggers_second_update(self, scene_manager):
        """When start_scene is called during update, the new scene should get a second update with empty events."""
        scene1 = StubGameObject()
        scene2 = StubGameObject()

        scene_manager.start_scene(scene1, 0)

        # First update at t=0
        scene_manager.update(0, [])
        assert scene1.update_times == [0]
        assert scene2.update_times == []

        # Second update where scene1 switches to scene2
        def scene1_update_with_switch(current_time, events):
            scene1.update_times.append(current_time)
            scene1.update_events_list.append(events)
            scene_manager.start_scene(scene2, None)  # Use stored global_time

        original_update = scene1.update
        scene1.update = scene1_update_with_switch

        scene_manager.update(1000, ['event1', 'event2'])

        scene1.update = original_update

        # scene1 was updated with events
        assert scene1.update_times == [0, 1000]
        assert scene1.update_events_list == [[], ['event1', 'event2']]

        # scene2 was created and got a second update with empty events
        # scene2's context was created with start_time = 1000 (current global_time)
        # local_time = 1000 - 1000 - 0 = 0
        assert scene2.update_times == [0]
        assert scene2.update_events_list == [[]]  # Empty events
