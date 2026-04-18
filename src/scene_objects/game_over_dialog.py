from engine.modal import Modal
from scene_objects.button import Button
from scene_objects.views.game_over_dialog_view import GameOverDialogView


class GameOverDialog(Modal):
    def __init__(
        self, *, uptime, stage_name, score, restart_game_fn, main_menu_fn, standalone=False
    ):
        self.uptime = uptime
        self.score = score
        self.stage_name = stage_name
        self.standalone = standalone
        super().__init__(GameOverDialogView(self))

        self._play_again_button = Button('Play Again', restart_game_fn)
        self.children.append(self._play_again_button)

        if not self.standalone:
            self._main_menu_button = Button('Main Menu', main_menu_fn)
            self.children.append(self._main_menu_button)

