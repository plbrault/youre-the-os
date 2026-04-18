import pytest

from engine.modal import Modal
from engine.modal_view import ModalView
from scene_objects.button import Button


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


class TestModal:
    @pytest.fixture
    def modal(self):
        return StubModal()

    def test_close_calls_scene_close_modal(self, modal):
        class FakeScene:
            close_modal_called = False
            def close_modal(self):
                self.close_modal_called = True

        modal.scene = FakeScene()
        modal.close()

        assert modal.scene.close_modal_called

    def test_close_without_scene_does_not_crash(self, modal):
        modal.scene = None
        modal.close()

    def test_children_can_be_added(self, modal):
        button = Button('Test', lambda: None)
        modal.children.append(button)

        assert button in modal.children
