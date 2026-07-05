from engine.game_event import GameEvent
from engine.game_event_type import GameEventType
from scene_objects.story_stage_defeat_dialog import StoryStageDefeatDialog


def _make_dialog(*, reason='Defeated', standalone=False):
    restart_calls = []
    main_menu_calls = []

    def restart_stage_fn():
        restart_calls.append(True)

    def main_menu_fn():
        main_menu_calls.append(True)

    dialog = StoryStageDefeatDialog(
        uptime='0:00:00',
        stage_name='Stage 1: 1998',
        score=0,
        reason=reason,
        restart_stage_fn=restart_stage_fn,
        main_menu_fn=main_menu_fn,
        standalone=standalone,
    )
    dialog.view.set_xy(0, 0)
    return dialog, restart_calls, main_menu_calls


def _click(button):
    center = (
        button.view.x + button.view.width / 2,
        button.view.y + button.view.height / 2,
    )
    button.update(0, [GameEvent(GameEventType.MOUSE_LEFT_CLICK, {'position': center})])


class TestStoryStageDefeatDialog:
    def test_primary_button_is_try_again(self):
        dialog, _, _ = _make_dialog()
        assert dialog.primary_button.text == 'Try Again'

    def test_main_menu_button_label(self):
        dialog, _, _ = _make_dialog()
        assert dialog.main_menu_button.text == 'Main Menu'

    def test_primary_button_calls_restart(self):
        dialog, restart_calls, _ = _make_dialog()
        _click(dialog.primary_button)
        assert restart_calls == [True]

    def test_main_menu_button_calls_main_menu_fn(self):
        dialog, _, main_menu_calls = _make_dialog()
        _click(dialog.main_menu_button)
        assert main_menu_calls == [True]

    def test_main_menu_button_present_in_children(self):
        dialog, _, _ = _make_dialog()
        assert dialog.primary_button in dialog.children
        assert dialog.main_menu_button in dialog.children

    def test_standalone_keeps_primary_button_in_children(self):
        dialog, _, _ = _make_dialog(standalone=True)
        assert dialog.primary_button in dialog.children
        assert dialog.main_menu_button not in dialog.children

    def test_height_includes_reason_when_present(self):
        dialog_without_reason, _, _ = _make_dialog(reason=None)
        dialog_with_reason, _, _ = _make_dialog(reason='Defeated')
        assert dialog_with_reason.view.height > dialog_without_reason.view.height

    def test_standalone_height_equals_non_standalone_height(self):
        standalone_dialog, _, _ = _make_dialog(standalone=True)
        non_standalone_dialog, _, _ = _make_dialog(standalone=False)
        assert standalone_dialog.view.height == non_standalone_dialog.view.height
