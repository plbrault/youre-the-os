from lib.game_event_type import GameEventType
from lib.game_object import GameObject
from game_objects.views.button_view import ButtonView

class Button(GameObject):  
    
    def __init__(self, text, action_fn):
        super().__init__(ButtonView(self))
        self.text = text
        self._action_fn = action_fn
    