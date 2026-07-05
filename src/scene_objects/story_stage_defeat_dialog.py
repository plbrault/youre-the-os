from engine.modal import Modal
from scene_objects.button import Button
from scene_objects.views.story_stage_defeat_dialog_view import StoryStageDefeatDialogView


class StoryStageDefeatDialog(Modal):
    def __init__(
        self, *, uptime, stage_name, score, reason=None, restart_stage_fn,
        main_menu_fn, standalone=False,
    ):
        self.uptime = uptime
        self.stage_name = stage_name
        self.score = score
        self.reason = reason
        self.standalone = standalone
        super().__init__(StoryStageDefeatDialogView(self))

        self.primary_button = Button('Try Again', restart_stage_fn)
        self.children.append(self.primary_button)
        self.main_menu_button = Button('Main Menu', main_menu_fn)
        if not self.standalone:
            self.children.append(self.main_menu_button)
