from engine.modal import Modal
from scene_objects.button import Button
from scene_objects.views.story_stage_result_dialog_view import StoryStageResultDialogView


def _no_op():
    pass


class StoryStageResultDialog(Modal):
    def __init__(
        self, *, is_victory, uptime, stage_name, score,
        reason=None, restart_game_fn, main_menu_fn, standalone=False
    ):
        self.is_victory = is_victory
        self.uptime = uptime
        self.stage_name = stage_name
        self.score = score
        self.reason = reason
        self.standalone = standalone
        super().__init__(StoryStageResultDialogView(self))

        if is_victory:
            self.primary_button = Button('Next Stage', _no_op)
        else:
            self.primary_button = Button('Try Again', restart_game_fn)
        self.children.append(self.primary_button)

        main_menu_action = _no_op if standalone else main_menu_fn
        self.main_menu_button = Button('Main Menu', main_menu_action)
        self.children.append(self.main_menu_button)
