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
        super().__init__('test')

    def setup(self):
        self._scene_objects = []

    def update(self, current_time, events):
        for scene_object in self._scene_objects:
            scene_object.update(current_time, events)


class SetupTrackingScene(Scene):
    def __init__(self):
        self.setup_call_count = 0
        super().__init__('test')

    def setup(self):
        self.setup_call_count += 1
        self._scene_objects = []

    def update(self, current_time, events):
        for scene_object in self._scene_objects:
            scene_object.update(current_time, events)


class TestSceneModalLifecycle:
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

    def test_show_modal_appends_to_scene_objects(self, scene, modal):
        scene.show_modal(modal)

        assert modal in scene._scene_objects

    def test_modal_property_returns_active_modal(self, scene, modal):
        scene.show_modal(modal)

        assert scene.modal is modal

    def test_modal_property_none_when_no_modal(self, scene):
        assert scene.modal is None

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

        assert scene.modal is None

    def test_close_modal_calls_modal_on_close(self, scene, modal):
        scene.show_modal(modal)
        scene.close_modal()

        assert modal.on_close_called

    def test_modal_close_triggers_close_modal(self, scene, modal):
        scene.show_modal(modal)
        modal.close()

        assert scene.modal is None

    def test_show_modal_only_one_at_a_time(self, scene, modal):
        scene.show_modal(modal)

        second_modal = StubModal()
        with pytest.raises(RuntimeError):
            scene.show_modal(second_modal)

    def test_close_modal_without_modal_does_not_crash(self, scene):
        scene.close_modal()


class TestSceneReset:
    @pytest.fixture
    def scene(self):
        scene = SetupTrackingScene()
        scene.scene_manager = type('FakeSceneManager', (), {
            'screen': __import__('pygame').Surface(WINDOW_SIZE)
        })()
        scene.setup()
        return scene

    def test_reset_calls_setup(self, scene):
        initial_count = scene.setup_call_count
        scene.reset()

        assert scene.setup_call_count == initial_count + 1

    def test_reset_closes_active_modal(self, scene):
        scene.show_modal(StubModal())
        scene.reset()

        assert scene.modal is None

    def test_reset_works_with_no_modal(self, scene):
        scene.reset()

        assert scene.modal is None
        assert scene.setup_call_count == 2
