from lib.game_object import GameObject
from game_objects.button import Button
from game_objects.views.game_over_dialog_view import GameOverDialogView

class GameOverDialog(GameObject):
    
    def __init__(self, uptime, score):
        self.uptime = uptime
        self.score = score
        super().__init__(GameOverDialogView(self))
        
        self._tryAgainButton = Button('Try Again', lambda x: x)
                
        self.children.append(self._tryAgainButton)

    def update(self, current_time, events):
        self._tryAgainButton.view.set_xy(self.view.x + 20, self.view.y + self.view.height - 80)
        
        for child in self.children:
            child.update(current_time, events)
    