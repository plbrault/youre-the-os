from lib.game_object import GameObject
from game_objects.views.game_over_dialog_view import GameOverDialogView

class GameOverDialog(GameObject):
    def __init__(self, text = ''):
        super().__init__(GameOverDialogView(self))

    def update(self, current_time, events):
        pass
    