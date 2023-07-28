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
        
        self._num_processes_selector = OptionSelector([str(i) for i in range(1, 37)], self._config['num_processes_at_startup'] - 1)
        self.children.append(self._num_processes_selector)
        
        self._num_ram_rows_selector = OptionSelector([str(i) for i in range(1, 14)], self._config['num_ram_rows'] - 1)
        self.children.append(self._num_ram_rows_selector)
        
        self._new_process_probability_selector = OptionSelector([str(i) + ' %' for i in range(0, 105, 5)])
        self._new_process_probability_selector.selected_option = str(int(self._config['new_process_probability'] * 100)) + ' %'
        self.children.append(self._new_process_probability_selector)
        
        self._io_probability_selector = OptionSelector([str(i) + ' %' for i in range(0, 55, 5)])
        self._io_probability_selector.selected_option = str(int(self._config['io_probability'] * 100)) + ' %'
        self.children.append(self._io_probability_selector)
        
        selector_width = self._new_process_probability_selector.view.width
        self._num_cpus_selector.view.min_width = selector_width
        self._num_processes_selector.view.min_width = selector_width
        self._num_ram_rows_selector.view.min_width = selector_width
        self._io_probability_selector.view.min_width = selector_width

    def update(self, current_time, events):
        self._num_cpus_selector.view.set_xy(
            self.view.x + self.view.width - self._num_cpus_selector.view.width - 10,
            self.view.num_cpus_y + (self.view.label_height - self._num_cpus_selector.view.height) / 2
        )
        self._num_processes_selector.view.set_xy(
            self.view.x + self.view.width - self._num_processes_selector.view.width - 10,
            self.view.num_processes_y + (self.view.label_height - self._num_processes_selector.view.height) / 2
        )
        self._num_ram_rows_selector.view.set_xy(
            self.view.x + self.view.width - self._num_ram_rows_selector.view.width - 10,
            self.view.num_ram_rows_y + (self.view.label_height - self._num_ram_rows_selector.view.height) / 2
        )
        self._new_process_probability_selector.view.set_xy(
            self.view.x + self.view.width - self._new_process_probability_selector.view.width - 10,
            self.view.new_process_probability_y + (self.view.label_height - self._new_process_probability_selector.view.height) / 2
        )
        self._io_probability_selector.view.set_xy(
            self.view.x + self.view.width - self._io_probability_selector.view.width - 10,
            self.view.io_probability_y + (self.view.label_height - self._io_probability_selector.view.height) / 2
        )
        
        for child in self.children:
            child.update(current_time, events)
    