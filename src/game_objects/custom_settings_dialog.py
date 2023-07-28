from difficulty_levels import default_difficulty
from lib.game_object import GameObject
from game_objects.button import Button
from game_objects.option_selector import OptionSelector
from game_objects.views.custom_settings_dialog_view import CustomSettingsDialogView

class CustomSettingsDialog(GameObject):
    
    def __init__(self):
        super().__init__(CustomSettingsDialogView(self))
        
        self._config = default_difficulty['config']
        
        self._num_cpus_selector = OptionSelector([str(i) for i in range(1, 13)], self._config['num_cpus'] - 1)
        self.children.append(self._num_cpus_selector)

    def update(self, current_time, events):
        self._num_cpus_selector.view.set_xy(
            self.view.x + self.view.width - self._num_cpus_selector.view.width - 10,
            self.view.num_cpus_y + (self.view.num_cpus_height - self._num_cpus_selector.view.height) / 2
        )
        
        for child in self.children:
            child.update(current_time, events)
    