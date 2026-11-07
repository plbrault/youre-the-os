import pytest

from engine.player_input import PlayerInput
from engine.player_input_type import PlayerInputType
from scene_objects.in_game_menu_dialog import InGameMenuDialog


def _make_dialog(scene=None):
    restart_calls = []
    main_menu_calls = []
    hotkeys_calls = []

    def restart_stage_fn():
        restart_calls.append(True)

    def main_menu_fn():
        main_menu_calls.append(True)

    def hotkeys_fn():
        hotkeys_calls.append(True)

    dialog = InGameMenuDialog(
        restart_stage_fn,
        main_menu_fn,
        hotkeys_fn,
    )
    dialog.scene = scene
    dialog.view.set_xy(0, 0)
    return dialog, restart_calls, main_menu_calls, hotkeys_calls


def _click(button):
    center = (
        button.view.x + button.view.width / 2,
        button.view.y + button.view.height / 2,
    )
    button.update(0, [PlayerInput(PlayerInputType.MOUSE_LEFT_CLICK, {'position': center})])


class TestInGameMenuDialog:
    @pytest.fixture
    def fake_scene(self):
        class FakeScene:
            close_modal_called = False

            def close_modal(self):
                self.close_modal_called = True

        return FakeScene()

    def test_restart_button_label(self):
        dialog, _, _, _ = _make_dialog()
        assert dialog.restart_button.text == 'Restart Game'

    def test_main_menu_button_label(self):
        dialog, _, _, _ = _make_dialog()
        assert dialog.main_menu_button.text == 'Return to Main Menu'

    def test_hotkeys_button_label(self):
        dialog, _, _, _ = _make_dialog()
        assert dialog.hotkeys_button.text == 'Hotkeys'

    def test_close_button_label(self):
        dialog, _, _, _ = _make_dialog()
        assert dialog.close_menu_button.text == 'Close'

    def test_restart_button_calls_restart_stage_fn(self):
        dialog, restart_calls, main_menu_calls, hotkeys_calls = _make_dialog()
        _click(dialog.restart_button)

        assert restart_calls == [True]
        assert main_menu_calls == []
        assert hotkeys_calls == []

    def test_main_menu_button_calls_main_menu_fn(self):
        dialog, restart_calls, main_menu_calls, hotkeys_calls = _make_dialog()
        _click(dialog.main_menu_button)

        assert restart_calls == []
        assert main_menu_calls == [True]
        assert hotkeys_calls == []

    def test_hotkeys_button_calls_hotkeys_fn(self):
        dialog, restart_calls, main_menu_calls, hotkeys_calls = _make_dialog()
        _click(dialog.hotkeys_button)

        assert restart_calls == []
        assert main_menu_calls == []
        assert hotkeys_calls == [True]

    def test_close_button_calls_close_modal_on_scene(self, fake_scene):
        dialog, _, _, _ = _make_dialog(fake_scene)
        _click(dialog.close_menu_button)

        assert fake_scene.close_modal_called

    def test_buttons_present_in_children(self):
        dialog, _, _, _ = _make_dialog()
        assert dialog.restart_button in dialog.children
        assert dialog.main_menu_button in dialog.children
        assert dialog.hotkeys_button in dialog.children
        assert dialog.close_menu_button in dialog.children

    def test_update_forwards_player_inputs_to_buttons(self):
        dialog, _, main_menu_calls, _ = _make_dialog()
        center = (
            dialog.main_menu_button.view.x + dialog.main_menu_button.view.width / 2,
            dialog.main_menu_button.view.y + dialog.main_menu_button.view.height / 2,
        )
        dialog.update(0, [PlayerInput(PlayerInputType.MOUSE_LEFT_CLICK, {'position': center})])

        assert main_menu_calls == [True]
