from config.stage_config import StageConfig
from scenes.stage import Stage
from scene_objects.stage_intro_dialog import Badge, Section, StageIntroDialog
from scene_objects.story_stage_defeat_dialog import StoryStageDefeatDialog
from scene_objects.story_stage_victory_dialog import StoryStageVictoryDialog


class StoryStage(Stage):
    stage_name: str = ''
    victory_time_ms: int = 0
    intro_sections: tuple[Section, ...] = ()
    intro_badges: tuple[Badge, ...] = ()

    def __init__(self, config: StageConfig):
        super().__init__(self.stage_name, config)

    def check_victory(self) -> bool:
        return self.uptime_manager.uptime_ms >= self.victory_time_ms

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
