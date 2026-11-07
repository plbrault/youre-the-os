import pytest

from engine.modal import Modal
from engine.modal_view import ModalView
from engine.scene import Scene
from engine.scene_manager import SceneManager
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
    def scene_manager(self):
        import pygame
        manager = SceneManager()
        manager.screen = pygame.Surface(WINDOW_SIZE)
        return manager

    @pytest.fixture
    def scene(self, scene_manager):
        scene = StubScene()
        scene_manager.register_scene(scene)
        scene_manager.start_scene(scene, 0)
        return scene

    @pytest.fixture
    def modal(self):
        return StubModal()

    def test_active_modal_returns_opened_modal(self, scene, modal):
        scene.open_modal(modal)

        assert scene.active_modal is modal

    def test_open_modal_pushes_modal_as_top_context(self, scene, modal):
        scene.open_modal(modal)

        assert scene.scene_manager.get_top_context() is modal

    def test_close_modal_restores_scene_as_top_context(self, scene, modal):
        scene.open_modal(modal)
        scene.close_modal()

        assert scene.scene_manager.get_top_context() is scene

    def test_active_modal_none_when_no_modal(self, scene):
        assert scene.active_modal is None

    def test_open_modal_centers_modal_on_screen(self, scene, modal):
        scene.open_modal(modal)
        screen_width = WINDOW_SIZE[0]
        screen_height = WINDOW_SIZE[1]

        assert modal.view.x == (screen_width - modal.view.width) / 2
        assert modal.view.y == (screen_height - modal.view.height) / 2

    def test_open_modal_sets_scene_reference(self, scene, modal):
        scene.open_modal(modal)

        assert modal.scene is scene

    def test_close_modal_clears_active_modal(self, scene, modal):
        scene.open_modal(modal)
        scene.close_modal()

        assert scene.active_modal is None

    def test_active_modal_close_triggers_close_modal(self, scene, modal):
        scene.open_modal(modal)
        modal.close()

        assert scene.active_modal is None

    def test_opening_second_modal_makes_it_active_modal(self, scene, modal):
        scene.open_modal(modal)

        second_modal = StubModal()
        scene.open_modal(second_modal)

        assert scene.active_modal is second_modal

    def test_opening_second_modal_makes_it_top_context(self, scene, modal):
        scene.open_modal(modal)

        second_modal = StubModal()
        scene.open_modal(second_modal)

        top_context = scene.scene_manager.get_top_context()
        assert top_context is second_modal

    def test_closing_active_modal_reveals_underlying_modal(self, scene, modal):
        scene.open_modal(modal)
        scene.open_modal(StubModal())
        scene.close_modal()

        assert scene.active_modal is modal
        assert scene.scene_manager.get_top_context() is modal

    def test_active_modal_close_reveals_underlying_modal(self, scene, modal):
        scene.open_modal(modal)
        top_modal = StubModal()
        scene.open_modal(top_modal)
        top_modal.close()

        assert scene.active_modal is modal
        assert scene.scene_manager.get_top_context() is modal

    def test_close_modal_without_modal_does_not_crash(self, scene):
        scene.close_modal()


class TestSceneReset:
    @pytest.fixture
    def scene_manager(self):
        import pygame
        manager = SceneManager()
        manager.screen = pygame.Surface(WINDOW_SIZE)
        return manager

    @pytest.fixture
    def scene(self, scene_manager):
        scene = SetupTrackingScene()
        scene_manager.register_scene(scene)
        scene_manager.start_scene(scene, 0)
        return scene

    def test_reset_calls_setup(self, scene):
        initial_count = scene.setup_call_count
        scene.reset()

        assert scene.setup_call_count == initial_count + 1

    def test_reset_closes_active_modal(self, scene):
        scene.open_modal(StubModal())
        scene.reset()

        assert scene.active_modal is None

    def test_reset_closes_all_active_modals(self, scene):
        scene.open_modal(StubModal())
        scene.open_modal(StubModal())
        scene.reset()

        assert scene.active_modal is None

    def test_reset_works_with_no_modal(self, scene):
        scene.reset()

        assert scene.active_modal is None
        assert scene.setup_call_count == 2
