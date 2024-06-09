from engine.game_object import GameObject
from game_objects.button import Button
from game_objects.views.game_over_dialog_view import GameOverDialogView


class GameOverDialog(GameObject):
    def __init__(self, uptime, stage_name, score, restart_game_fn, main_menu_fn, standalone=False):
        self.uptime = uptime
        self.score = score
        self.stage_name = stage_name
        self.standalone = standalone
        super().__init__(GameOverDialogView(self))

        if not self.standalone:
            self._play_again_button = Button('Play Again', restart_game_fn)
            self._main_menu_button = Button('Main Menu', main_menu_fn)

            self.children.append(self._play_again_button)
            self.children.append(self._main_menu_button)

    def update(self, current_time, events):
        if not self.standalone:
            self._play_again_button.view.set_xy(
                self.view.x + (self.view.width / 2) -
                self._play_again_button.view.width - 10,
                self.view.y + self.view.height - self._play_again_button.view.height - 20
            )
            self._main_menu_button.view.set_xy(
                self.view.x + (self.view.width / 2) + 10,
                self.view.y + self.view.height - self._play_again_button.view.height - 20
            )

        for child in self.children:
            child.update(current_time, events)
