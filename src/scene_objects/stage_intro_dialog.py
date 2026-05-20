from engine.modal import Modal
from scene_objects.button import Button
from scene_objects.views.stage_intro_dialog_view import StageIntroDialogView


class StageIntroDialog(Modal):
    def __init__(self, title, sections):
        self.title = title
        self.sections = sections
        super().__init__(StageIntroDialogView(self))

        self.start_button = Button('Start', self.close)
        self.children.append(self.start_button)
