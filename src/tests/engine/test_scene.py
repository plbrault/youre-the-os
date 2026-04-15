import pytest

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
        self.on_open_called = False
        self.on_close_called = False
        super().__init__(StubModalView())

    def on_open(self):
        self.on_open_called = True

    def on_close(self):
        self.on_close_called = True


class StubScene(Scene):
    def __init__(self):
        self._update_called = False
        self._pause_called = False
        self._unpause_called = False
        super().__init__('test')

    def setup(self):
        self._scene_objects = []

    def _update(self, current_time, events):
        self._update_called = True
        for scene_object in self._scene_objects:
            scene_object.update(current_time, events)

    def _pause(self):
        self._pause_called = True

    def _unpause(self):
        self._unpause_called = True


class TestSceneModalIntegration:
    @pytest.fixture
    def scene(self):
        scene = StubScene()
        scene.scene_manager = type('FakeSceneManager', (), {
            'screen': __import__('pygame').Surface(WINDOW_SIZE)
        })()
        scene.setup()
        return scene

    @pytest.fixture
    def modal(self):
        return StubModal()

    def test_update_without_modal_calls_update(self, scene):
        scene.update(0, [])

        assert scene._update_called

    def test_update_with_modal_routes_events_to_modal(self, scene, modal):
        scene.show_modal(modal)

        modal_updated = False
        original_update = modal.update

        def spy_update(current_time, events):
            nonlocal modal_updated
            modal_updated = True
            original_update(current_time, events)

        modal.update = spy_update
        scene.update(0, [])

        assert modal_updated
        assert not scene._update_called

    def test_show_modal_appends_to_scene_objects(self, scene, modal):
        scene.show_modal(modal)

        assert modal in scene._scene_objects

    def test_show_modal_sets_modal_reference(self, scene, modal):
        scene.show_modal(modal)

        assert scene._modal is modal

    def test_show_modal_calls_pause(self, scene, modal):
        scene.show_modal(modal)

        assert scene._pause_called

    def test_show_modal_calls_modal_on_open(self, scene, modal):
        scene.show_modal(modal)

        assert modal.on_open_called

    def test_show_modal_centers_modal_on_screen(self, scene, modal):
        scene.show_modal(modal)
        screen_width = WINDOW_SIZE[0]
        screen_height = WINDOW_SIZE[1]

        assert modal.view.x == (screen_width - modal.view.width) / 2
        assert modal.view.y == (screen_height - modal.view.height) / 2

    def test_show_modal_sets_scene_reference(self, scene, modal):
        scene.show_modal(modal)

        assert modal.scene is scene

    def test_close_modal_removes_from_scene_objects(self, scene, modal):
        scene.show_modal(modal)
        scene.close_modal()

        assert modal not in scene._scene_objects

    def test_close_modal_clears_modal_reference(self, scene, modal):
        scene.show_modal(modal)
        scene.close_modal()

        assert scene._modal is None

    def test_close_modal_calls_unpause(self, scene, modal):
        scene.show_modal(modal)
        scene.close_modal()

        assert scene._unpause_called

    def test_close_modal_calls_modal_on_close(self, scene, modal):
        scene.show_modal(modal)
        scene.close_modal()

        assert modal.on_close_called

    def test_modal_close_triggers_close_modal(self, scene, modal):
        scene.show_modal(modal)
        modal.close()

        assert scene._modal is None

    def test_show_modal_only_one_at_a_time(self, scene, modal):
        scene.show_modal(modal)

        second_modal = StubModal()
        with pytest.raises(RuntimeError):
            scene.show_modal(second_modal)

    def test_close_modal_without_modal_does_not_crash(self, scene):
        scene.close_modal()
