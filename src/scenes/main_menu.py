from difficulty_levels import DifficultyLevel, difficulty_levels
from engine.scene import Scene
from game_objects.about_dialog import AboutDialog
from game_objects.button import Button
from game_objects.custom_settings_dialog import CustomSettingsDialog
from game_objects.hotkey_dialog import HokeyDialog
from game_objects.main_menu_title import MainMenuTitle
from game_objects.difficulty_selection_label import DifficultySelectionLabel
from game_objects.option_selector import OptionSelector
from stage_config import StageConfig


class MainMenu(Scene):
    def __init__(self):
        super().__init__('main_menu')
        self._selected_difficulty_id = None
        self._custom_config = StageConfig()

        self._difficulty_selector = None
        self._custom_settings_dialog = None
        self._about_dialog = None
        self._hotkey_dialog = None

    def setup(self):
        self._scene_objects = []

        title = MainMenuTitle()
        title.view.set_xy(0, 50)
        self._scene_objects.append(title)

        difficulty_selection_label = DifficultySelectionLabel()
        difficulty_selection_label.view.set_xy(
            (self.screen.get_width() - difficulty_selection_label.view.width) / 2,
            title.view.y + title.view.height + 50)
        self._scene_objects.append(difficulty_selection_label)

        difficulty_level_names = list(
            map(lambda difficulty_level: difficulty_level.name, difficulty_levels))
        difficulty_level_names.append('Custom')
        self._difficulty_selector = OptionSelector(difficulty_level_names, 1)
        self._difficulty_selector.view.set_xy(
            (self.screen.get_width() - self._difficulty_selector.view.width) / 2,
            difficulty_selection_label.view.y + difficulty_selection_label.view.height + 20)
        self._scene_objects.append(self._difficulty_selector)

        play_button = Button('Play', self._on_start_button_click)
        play_button.view.set_xy(
            (self.screen.get_width() - play_button.view.width) / 2,
            self._difficulty_selector.view.y + self._difficulty_selector.view.height + 20)
        self._scene_objects.append(play_button)

        how_to_play_button = Button('How to Play', self._start_how_to_play)
        how_to_play_button.view.set_xy(
            150,
            self.screen.get_height() - how_to_play_button.view.height - 100
        )
        self._scene_objects.append(how_to_play_button)

        hotkey_button = Button(
            'Hotkeys', self._open_hotkey_dialog)
        hotkey_button.view.set_xy(
            how_to_play_button.view.x + how_to_play_button.view.width + 20,
            self.screen.get_height() - hotkey_button.view.height - 100
        )
        self._scene_objects.append(hotkey_button)

        about_button = Button('About', self._open_about_dialog)
        about_button.view.set_xy(
            self.screen.get_width() - about_button.view.width - 150,
            self.screen.get_height() - about_button.view.height - 100
        )
        self._scene_objects.append(about_button)

        self._custom_settings_dialog = None

        if self._selected_difficulty_id is not None:
            self._difficulty_selector.selected_option_id = self._selected_difficulty_id

    def _on_start_button_click(self):
        self._selected_difficulty_id = self._difficulty_selector.selected_option_id
        if self._selected_difficulty_id == len(difficulty_levels):
            self._open_custom_settings_dialog()
        else:
            difficulty_level = difficulty_levels[self._selected_difficulty_id]
            self._start_game(difficulty_level)

    def _open_custom_settings_dialog(self):
        self._custom_settings_dialog = CustomSettingsDialog(
            lambda: self._start_game(
                DifficultyLevel(
                    'Custom',
                    self._custom_settings_dialog.config
                )
            ),
            self._close_custom_settings_dialog,
            self._custom_config
        )
        self._custom_settings_dialog.view.set_xy(
            self.screen.get_width() / 2 - self._custom_settings_dialog.view.width / 2,
            self.screen.get_height() / 2 - self._custom_settings_dialog.view.height / 2)
        self._scene_objects.append(self._custom_settings_dialog)

    def _open_about_dialog(self):
        self._about_dialog = AboutDialog(self._close_about_dialog)
        self._about_dialog.view.set_xy(
            self.screen.get_width() / 2 - self._about_dialog.view.width / 2,
            self.screen.get_height() / 2 - self._about_dialog.view.height / 2
        )
        self._scene_objects.append(self._about_dialog)

    def _close_about_dialog(self):
        self._scene_objects.remove(self._about_dialog)
        self._about_dialog = None

    def _open_hotkey_dialog(self):
        self._hotkey_dialog = HokeyDialog(
            self._close_hotkey_dialog)
        self._hotkey_dialog.view.set_xy(
            self.screen.get_width() / 2 - self._hotkey_dialog.view.width / 2,
            self.screen.get_height() / 2 - self._hotkey_dialog.view.height / 2)
        self._scene_objects.append(self._hotkey_dialog)

    def _close_custom_settings_dialog(self):
        self._scene_objects.remove(self._custom_settings_dialog)
        self._custom_settings_dialog = None

    def _close_hotkey_dialog(self):
        self._scene_objects.remove(self._hotkey_dialog)
        self._hotkey_dialog = None

    def _start_game(self, difficulty_level):
        if self._custom_settings_dialog is not None:
            self._custom_config = self._custom_settings_dialog.config
        self.scene_manager.get_scene('stage').name = 'Difficulty: ' + difficulty_level.name.upper()
        self.scene_manager.get_scene('stage').config = difficulty_level.config
        self.scene_manager.start_scene('stage')

    def _start_how_to_play(self):
        self.scene_manager.start_scene('how_to_play')

    def update(self, current_time, events):
        if self._about_dialog is not None:
            self._about_dialog.update(current_time, events)
        elif self._custom_settings_dialog is not None:
            self._custom_settings_dialog.update(current_time, events)
        elif self._hotkey_dialog is not None:
            self._hotkey_dialog.update(current_time, events)
        else:
            for game_object in self._scene_objects:
                game_object.update(current_time, events)
