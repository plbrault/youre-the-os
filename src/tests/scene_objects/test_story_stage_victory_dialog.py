from engine.game_event import GameEvent
from engine.game_event_type import GameEventType
from scene_objects.story_stage_victory_dialog import StoryStageVictoryDialog


def _make_dialog(*, standalone=False):
    next_stage_calls = []
    main_menu_calls = []

    def next_stage_fn():
        next_stage_calls.append(True)

    def main_menu_fn():
        main_menu_calls.append(True)

    dialog = StoryStageVictoryDialog(
        uptime='0:00:00',
        stage_name='Stage 1: 1998',
        score=0,
        next_stage_fn=next_stage_fn,
        main_menu_fn=main_menu_fn,
        standalone=standalone,
    )
    dialog.view.set_xy(0, 0)
    return dialog, next_stage_calls, main_menu_calls


def _click(button):
    center = (
        button.view.x + button.view.width / 2,
        button.view.y + button.view.height / 2,
    )
    button.update(0, [GameEvent(GameEventType.MOUSE_LEFT_CLICK, {'position': center})])


class TestStoryStageVictoryDialog:
    def test_primary_button_is_next_stage(self):
        dialog, _, _ = _make_dialog()
        assert dialog.primary_button.text == 'Next Stage'

    def test_main_menu_button_label(self):
        dialog, _, _ = _make_dialog()
        assert dialog.main_menu_button.text == 'Main Menu'

    def test_primary_button_calls_next_stage_fn(self):
        dialog, next_stage_calls, main_menu_calls = _make_dialog()
        _click(dialog.primary_button)
        assert next_stage_calls == [True]
        assert main_menu_calls == []

    def test_main_menu_button_calls_main_menu_fn(self):
        dialog, next_stage_calls, main_menu_calls = _make_dialog()
        _click(dialog.main_menu_button)
        assert next_stage_calls == []
        assert main_menu_calls == [True]

    def test_main_menu_button_present_in_children(self):
        dialog, _, _ = _make_dialog()
        assert dialog.primary_button in dialog.children
        assert dialog.main_menu_button in dialog.children

    def test_standalone_does_not_add_buttons_to_children(self):
        dialog, _, _ = _make_dialog(standalone=True)
        assert dialog.primary_button not in dialog.children
        assert dialog.main_menu_button not in dialog.children
