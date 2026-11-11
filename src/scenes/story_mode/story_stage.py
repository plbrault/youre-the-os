from config.stage_config import StageConfig
from constants import ONE_MINUTE
from scenes.stage import Stage
from scene_objects.process import ProcessType
from scene_objects.stage_intro_dialog import (
    Badge, KilledProcessBadge, Section, StageIntroDialog, TimerBadge,
)
from scene_objects.story_stage_defeat_dialog import StoryStageDefeatDialog
from scene_objects.story_stage_victory_dialog import StoryStageVictoryDialog


class VictoryCondition:
    """
    Base class for a condition of the story stages' victory conditions.

    A condition participating in a `StoryStage`'s `victory_conditions`
    contributes to the intro dialog and to the victory and defeat checks.
    """

    def check_victory(self, stage) -> bool: # pylint: disable=unused-argument
        return False

    def check_defeat(self, stage) -> str | None: # pylint: disable=unused-argument
        return None

    @property
    def intro_items(self) -> tuple[str, ...]:
        return ()

    @property
    def badges(self) -> tuple[Badge, ...]:
        return ()


class TimeVictoryCondition(VictoryCondition):
    def __init__(self, minutes: int):
        self.minutes = minutes

    def check_victory(self, stage) -> bool:
        return stage.uptime_manager.uptime_ms >= self.minutes * ONE_MINUTE

    @property
    def intro_items(self) -> tuple[str, ...]:
        return (f'Survive {self.minutes} minutes',)

    @property
    def badges(self) -> tuple[Badge, ...]:
        return (TimerBadge(self.minutes),)


class MaxTerminatedProcessVictoryCondition(VictoryCondition):
    ragequit_defeat_reason = 'Too many user ragequits.'
    high_priority_intro_item = 'Do not let the user kill a high-priority process'

    def __init__(self, max_terminated_process: int,
                 max_terminated_high_priority_process: int | float = float('inf')):
        self.max_terminated_process = max_terminated_process
        self.max_terminated_high_priority_process = max_terminated_high_priority_process

    @property
    def high_priority_defeat_reason(self) -> str:
        if self.max_terminated_high_priority_process == 0:
            return 'The user killed a high-priority process.'
        return 'The user killed too many high-priority processes.'

    def check_defeat(self, stage) -> str | None:
        terminated_processes = stage.process_manager.user_terminated_processes
        high_priority_count = sum(1 for process in terminated_processes
                             if process.type == ProcessType.HIGH_PRIORITY)
        if high_priority_count > self.max_terminated_high_priority_process:
            return self.high_priority_defeat_reason
        if (
            stage.process_manager.user_terminated_process_count
            >= self.max_terminated_process
        ):
            return self.ragequit_defeat_reason
        return None

    @property
    def intro_items(self) -> tuple[str, ...]:
        items = [f'less than {self.max_terminated_process} user ragequits']
        if self.max_terminated_high_priority_process == 0:
            items.append(self.high_priority_intro_item)
        return tuple(items)

    @property
    def badges(self) -> tuple[Badge, ...]:
        badges = [KilledProcessBadge(f'<{self.max_terminated_process}')]
        if self.max_terminated_high_priority_process == 0:
            badges.append(KilledProcessBadge('0', is_high_priority=True))
        elif self.max_terminated_high_priority_process < float('inf'):
            badges.append(KilledProcessBadge(
                f'<{self.max_terminated_high_priority_process + 1}', is_high_priority=True))
        return tuple(badges)


class SurvivalVictoryCondition(VictoryCondition):
    """
    Combines a TimeVictoryCondition and a MaxTerminatedProcessVictoryCondition
    into a single condition, rendering the combined intro item that the
    'Victory Conditions' section displays for both together. Items beyond
    this combined item are mirrored from the latter condition, so the
    displayed high-priority rule always matches its limits and badges.
    """

    def __init__(self, minutes: int, max_terminated_process: int,
                 max_terminated_high_priority_process: int | float = float('inf')):
        self._time_condition = TimeVictoryCondition(minutes)
        self._max_condition = MaxTerminatedProcessVictoryCondition(
            max_terminated_process, max_terminated_high_priority_process)

    def check_victory(self, stage) -> bool:
        return self._time_condition.check_victory(stage)

    def check_defeat(self, stage) -> str | None:
        return self._max_condition.check_defeat(stage)

    @property
    def intro_items(self) -> tuple[str, ...]:
        time_item = self._time_condition.intro_items[0]
        ragequit_item = self._max_condition.intro_items[0]
        high_priority_items = self._max_condition.intro_items[1:]
        return (f'{time_item} with {ragequit_item}', *high_priority_items)

    @property
    def badges(self) -> tuple[Badge, ...]:
        return (*self._time_condition.badges, *self._max_condition.badges)


class StoryStage(Stage):
    """
    Base class for the stages of the game's story mode.

    A story stage is implemented by subclassing StoryStage and declaring
    its class attributes, then calling the parent constructor with its own
    stage config:

        class StoryStageX(StoryStage):
            stage_name = 'Stage X: Example'
            victory_conditions = _VICTORY_CONDITIONS
            intro_sections = _INTRO_SECTIONS

            def __init__(self):
                super().__init__(_STAGE_CONFIG)

    The `victory_conditions` attribute is a tuple of `VictoryCondition`.
    The `intro_sections` attribute is a tuple of `scene_objects.stage_intro_dialog.Section`.
    They are typically declared as module-level constants named `_VICTORY_CONDITIONS`
    and `_INTRO_SECTIONS`, along with `_STAGE_CONFIG` which is an instance
    of `config.stage_config.StageConfig`.

    The base class provides:
    * `check_victory` and `check_defeat`: checks derived from `victory_conditions`
    * `on_start`: a `scene_objects.stage_intro_dialog.StageIntroDialog`
      built from `intro_sections`, and a 'Victory Conditions' section and
      badges generated from `victory_conditions`, with a new instance
      created at each start or reset
    * `on_victory` / `on_defeat`: the story mode victory / defeat dialogs
    """
    stage_name: str = ''
    victory_conditions: tuple = ()
    intro_sections: tuple[Section, ...] = ()
    intro_badges: tuple[Badge, ...] = ()

    def __init__(self, config: StageConfig):
        super().__init__(self.stage_name, config)

    def check_victory(self) -> bool:
        if not self.victory_conditions:
            return False
        return all(condition.check_victory(self)
                   for condition in self.victory_conditions)

    def check_defeat(self) -> bool | tuple[bool, str]:
        for condition in self.victory_conditions:
            defeat_reason = condition.check_defeat(self)
            if defeat_reason is not None:
                return (True, defeat_reason)
        return False

    def on_start(self):
        sections = [*self.intro_sections]
        badges = [*self.intro_badges]
        if self.victory_conditions:
            items = []
            for condition in self.victory_conditions:
                items.extend(condition.intro_items)
                badges.extend(condition.badges)
            sections.append(Section('Victory Conditions', tuple(items)))
        self.open_modal(StageIntroDialog(
            self.name, tuple(sections), badges=tuple(badges)))

    def on_victory(self):
        self.open_modal(StoryStageVictoryDialog(
            uptime=self._uptime_manager.uptime_text,
            stage_name=self.name,
            score=self._score_manager.score,
            next_stage_fn=self._go_to_next_stage,
            main_menu_fn=self._return_to_main_menu,
            standalone=self._standalone,
        ))

    def _go_to_next_stage(self):
        pass

    def on_defeat(self, reason: str | None = None):
        self.open_modal(StoryStageDefeatDialog(
            uptime=self._uptime_manager.uptime_text,
            stage_name=self.name,
            score=self._score_manager.score,
            reason=reason,
            restart_stage_fn=self.reset,
            main_menu_fn=self._return_to_main_menu,
            standalone=self._standalone,
        ))
