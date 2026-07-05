from dataclasses import dataclass
from typing import TypeAlias

from engine.modal import Modal
from scene_objects.button import Button
from scene_objects.views.stage_intro_dialog_view import StageIntroDialogView


@dataclass(frozen=True)
class Section:
    heading: str
    items: tuple[str, ...]


@dataclass(frozen=True)
class KilledProcessBadge:
    text: str
    is_priority: bool = False


@dataclass(frozen=True)
class TimerBadge:
    minutes: int


Badge: TypeAlias = KilledProcessBadge | TimerBadge


class StageIntroDialog(Modal):
    def __init__(self, title: str, sections: tuple[Section, ...],
                 badges: tuple[Badge, ...] = ()) -> None:
        self.title = title
        self.sections = sections
        self.badges = badges
        super().__init__(StageIntroDialogView(self))

        self.start_button = Button('Start', self.close)
        self.children.append(self.start_button)
