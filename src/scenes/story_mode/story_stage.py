from config.stage_config import StageConfig
from scenes.stage import Stage
from scene_objects.stage_intro_dialog import Badge, Section, StageIntroDialog
from scene_objects.story_stage_defeat_dialog import StoryStageDefeatDialog
from scene_objects.story_stage_victory_dialog import StoryStageVictoryDialog


class StoryStage(Stage):
    """
    Base class for the stages of the game's story mode.

    A story stage is implemented by subclassing StoryStage and declaring
    its class attributes, then calling the parent constructor with its own
    stage config:

        class StoryStage3(StoryStage):
            stage_name = 'Stage 3: 2010'
            victory_time_ms = 6 * ONE_MINUTE
            intro_sections = _INTRO_SECTIONS
            intro_badges = _INTRO_BADGES

            def __init__(self):
                super().__init__(_STAGE_CONFIG)

    The intro attributes are tuples of `scene_objects.stage_intro_dialog.Section`
    and `scene_objects.stage_intro_dialog.Badge` objects. The config passed to
    the parent constructor is a `config.stage_config.StageConfig`. All are
    typically declared as module-level constants named `_INTRO_SECTIONS`,
    `_INTRO_BADGES` and `_STAGE_CONFIG`.

    The base class provides:
    * `check_victory`: a time-based victory condition, met when the stage
      uptime reaches `victory_time_ms`
    * `on_start`: a `scene_objects.stage_intro_dialog.StageIntroDialog`
      built from `intro_sections` and `intro_badges`, with a new instance
      created at each start or reset
    * `on_victory` / `on_defeat`: the story mode victory / defeat dialogs

    A subclass typically also overrides `check_defeat` to add stage-specific
    defeat conditions, calling super().check_defeat() to preserve the base
    user ragequit check, which returns `(True, 'Too many user ragequits.')`.
    Stage-specific conditions must themselves return a tuple `(True, reason)`
    so that the reason is displayed in the defeat dialog.
    """
    stage_name: str = ''
    victory_time_ms: int = 0
    intro_sections: tuple[Section, ...] = ()
    intro_badges: tuple[Badge, ...] = ()

    def __init__(self, config: StageConfig):
        super().__init__(self.stage_name, config)

    def check_victory(self) -> bool:
        return self.uptime_manager.uptime_ms >= self.victory_time_ms

    def check_defeat(self) -> bool | tuple[bool, str]:
        if super().check_defeat():
            return (True, 'Too many user ragequits.')
        return False

    def on_start(self):
        self.show_modal(StageIntroDialog(
            self.name,
            self.intro_sections,
            badges=self.intro_badges,
        ))

    def on_victory(self):
        self.show_modal(StoryStageVictoryDialog(
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
        self.show_modal(StoryStageDefeatDialog(
            uptime=self._uptime_manager.uptime_text,
            stage_name=self.name,
            score=self._score_manager.score,
            reason=reason,
            restart_stage_fn=self.reset,
            main_menu_fn=self._return_to_main_menu,
            standalone=self._standalone,
        ))
