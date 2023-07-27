from lib.game_object import GameObject
from game_objects.button import Button
from game_objects.views.game_over_dialog_view import GameOverDialogView

class GameOverDialog(GameObject):
    
    def __init__(self, uptime, score, restart_game_fn):
        self.uptime = uptime
        self.score = score
        super().__init__(GameOverDialogView(self))
        
        self._playAgainButton = Button('Play Again', restart_game_fn)
                
        self.children.append(self._playAgainButton)

    def update(self, current_time, events):
        if self._playAgainButton.view.x == 0:
            self._playAgainButton.view.set_xy(
                self.view.x + (self.view.width - self._playAgainButton.view.width) / 2,
                self.view.y + self.view.height - self._playAgainButton.view.height - 20
            )
        
        for child in self.children:
            child.update(current_time, events)
    