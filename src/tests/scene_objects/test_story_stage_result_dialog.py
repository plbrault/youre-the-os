from engine.game_event import GameEvent
from engine.game_event_type import GameEventType
from scene_objects.story_stage_result_dialog import StoryStageResultDialog


def _make_dialog(*, is_victory, standalone=False, reason=None):
    restart_calls = []
    main_menu_calls = []

    def restart_game_fn():
        restart_calls.append(True)

    def main_menu_fn():
        main_menu_calls.append(True)

    dialog = StoryStageResultDialog(
        is_victory=is_victory,
        uptime='0:00:00',
        stage_name='Stage 1: 1998',
        score=0,
        reason=reason,
        restart_game_fn=restart_game_fn,
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


class TestStoryStageResultDialog:
    def test_victory_primary_button_is_next_stage(self):
        dialog, _, _ = _make_dialog(is_victory=True)
        assert dialog.primary_button.text == 'Next Stage'

    def test_defeat_primary_button_is_try_again(self):
        dialog, _, _ = _make_dialog(is_victory=False, reason='Defeated')
        assert dialog.primary_button.text == 'Try Again'

    def test_main_menu_button_label(self):
        dialog, _, _ = _make_dialog(is_victory=True)
        assert dialog.main_menu_button.text == 'Main Menu'

    def test_victory_primary_button_is_no_op(self):
        dialog, restart_calls, main_menu_calls = _make_dialog(is_victory=True)
        _click(dialog.primary_button)
        assert restart_calls == []
        assert main_menu_calls == []

    def test_defeat_primary_button_calls_restart(self):
        dialog, restart_calls, _ = _make_dialog(is_victory=False, reason='Defeated')
        _click(dialog.primary_button)
        assert restart_calls == [True]

    def test_main_menu_button_calls_main_menu_fn_when_not_standalone(self):
        dialog, _, main_menu_calls = _make_dialog(
            is_victory=False, reason='Defeated', standalone=False)
        _click(dialog.main_menu_button)
        assert main_menu_calls == [True]

    def test_main_menu_button_is_no_op_when_standalone(self):
        dialog, _, main_menu_calls = _make_dialog(
            is_victory=False, reason='Defeated', standalone=True)
        _click(dialog.main_menu_button)
        assert main_menu_calls == []

    def test_main_menu_button_present_in_victory_children(self):
        dialog, _, _ = _make_dialog(is_victory=True)
        assert dialog.main_menu_button in dialog.children

    def test_main_menu_button_present_in_defeat_children(self):
        dialog, _, _ = _make_dialog(is_victory=False, reason='Defeated')
        assert dialog.main_menu_button in dialog.children

    def test_height_includes_reason_when_present(self):
        dialog_without_reason, _, _ = _make_dialog(is_victory=False, reason=None)
        dialog_with_reason, _, _ = _make_dialog(is_victory=False, reason='Defeated')
        assert dialog_with_reason.view.height > dialog_without_reason.view.height
