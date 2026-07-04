from engine.modal import Modal
from scene_objects.button import Button
from scene_objects.views.story_stage_victory_dialog_view import StoryStageVictoryDialogView


class StoryStageVictoryDialog(Modal):
    def __init__(
        self, *, uptime, stage_name, score, next_stage_fn, main_menu_fn,
        standalone=False,
    ):
        self.uptime = uptime
        self.stage_name = stage_name
        self.score = score
        self.standalone = standalone
        super().__init__(StoryStageVictoryDialogView(self))

        self.primary_button = Button('Next Stage', next_stage_fn)
        self.main_menu_button = Button('Main Menu', main_menu_fn)
        if not self.standalone:
            self.children.append(self.primary_button)
            self.children.append(self.main_menu_button)
