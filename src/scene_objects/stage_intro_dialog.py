from dataclasses import dataclass

from engine.modal import Modal
from scene_objects.button import Button
from scene_objects.views.stage_intro_dialog_view import StageIntroDialogView

@dataclass(frozen=True)
class Section:
    heading: str
    items: tuple[str, ...]

class StageIntroDialog(Modal):
    def __init__(self, title: str, sections: tuple[Section, ...]) -> None:
        self.title = title
        self.sections = sections
        super().__init__(StageIntroDialogView(self))

        self.start_button = Button('Start', self.close)
        self.children.append(self.start_button)
