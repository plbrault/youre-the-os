from lib.game_event_type import GameEventType
from lib.game_object import GameObject
from game_objects.views.option_selector_view import OptionSelectorView
from game_objects.button import Button

class OptionSelector(GameObject):  
    
    def __init__(self, options, default_option_id = 0):
        self._options = options
        self._selected_option_id = default_option_id
        super().__init__(OptionSelectorView(self))
        
        self._previous_button = Button('<', self._select_previous_option)
        self._children.append(self._previous_button)
        
        self._next_button = Button('>', self._select_next_option)
        self._children.append(self._next_button)
    
    @property
    def options(self):
        return self._options
    
    @property
    def selected_option_id(self):
        return self._selected_option_id
    
    @selected_option_id.setter
    def selected_option_id(self, value):
        self._selected_option_id = value
        
    @property
    def selected_option(self):
        return self._options[self.selected_option_id]
    
    @selected_option.setter
    def selected_option(self, value):
        self.selected_option_id = self._options.index(value) 
    
    @property
    def previous_button(self):
        return self._previous_button
    
    @property
    def next_button(self):
        return self._next_button 
    
    def _select_previous_option(self):
        if self.selected_option_id == 0:
            self.selected_option_id = len(self._options) - 1
        else:
            self.selected_option_id -= 1
            
    def _select_next_option(self):
        if self.selected_option_id == len(self._options) - 1:
            self.selected_option_id = 0
        else:
            self.selected_option_id += 1
    
    def update(self, current_time, events):
        self._previous_button.view.set_xy(self.view.x, self.view.y)
        self._next_button.view.set_xy(self.view.x + self.view.width - self._next_button.view.width, self.view.y)
        
        for child in self._children:
            child.update(current_time, events)
    