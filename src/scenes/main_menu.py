from os import path
import pygame
from random import randint

from difficulty_levels import difficulty_levels
from lib.scene import Scene
from game_objects.about_dialog import AboutDialog
from game_objects.button import Button
from game_objects.custom_settings_dialog import CustomSettingsDialog
from game_objects.key_binding_dialog import KeyBindingDialog
from game_objects.main_menu_title import MainMenuTitle
from game_objects.difficulty_selection_label import DifficultySelectionLabel
from game_objects.option_selector import OptionSelector

class MainMenu(Scene):
    def __init__(self, screen, scenes):
        super().__init__(screen, scenes)
        self._selected_difficulty_id = None
        self._custom_config = None
        
        self._custom_settings_dialog = None
        self._about_dialog = None
        self._key_binding_dialog = None
    
    def setup(self):
        self._scene_objects = []
        
        title = MainMenuTitle()
        title.view.set_xy(0, 50)
        self._scene_objects.append(title)
        
        difficulty_selection_label = DifficultySelectionLabel()
        difficulty_selection_label.view.set_xy(
            (self._screen.get_width() - difficulty_selection_label.view.width) / 2,
            title.view.y + title.view.height + 50
        )
        self._scene_objects.append(difficulty_selection_label)
        
        difficulty_level_names = list(map(lambda difficulty_level: difficulty_level['name'], difficulty_levels))
        difficulty_level_names.append('Custom')
        self._difficulty_selector = OptionSelector(difficulty_level_names, 1)
        self._difficulty_selector.view.set_xy(
            (self._screen.get_width() - self._difficulty_selector.view.width) / 2,
            difficulty_selection_label.view.y + difficulty_selection_label.view.height + 20
        )
        self._scene_objects.append(self._difficulty_selector)
        
        play_button = Button('Play', self._on_start_button_click)
        play_button.view.set_xy(
            (self._screen.get_width() - play_button.view.width) / 2,
            self._difficulty_selector.view.y + self._difficulty_selector.view.height + 20
        )
        self._scene_objects.append(play_button)
        
        how_to_play_button = Button('How to Play', self._start_how_to_play)
        how_to_play_button.view.set_xy(
            150,
            self._screen.get_height() - how_to_play_button.view.height - 100
        )
        self._scene_objects.append(how_to_play_button)
        
        key_binding_button = Button('Key Bindings', self._open_key_binding_dialog)
        key_binding_button.view.set_xy(
            how_to_play_button.view.x + how_to_play_button.view.width + 20,
            self._screen.get_height() - key_binding_button.view.height - 100
        )
        self._scene_objects.append(key_binding_button)        
        
        about_button = Button('About', self._open_about_dialog)
        about_button.view.set_xy(
            self._screen.get_width() - about_button.view.width - 150,
            self._screen.get_height() - about_button.view.height - 100
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
            self._start_game(difficulty_levels[self._difficulty_selector.selected_option_id]['config'])
            
    def _open_custom_settings_dialog(self):
        self._custom_settings_dialog = CustomSettingsDialog(
            lambda: self._start_game(self._custom_settings_dialog.config),
            self._close_custom_settings_dialog,
            self._custom_config
        )
        self._custom_settings_dialog.view.set_xy(
            self._screen.get_width() / 2 - self._custom_settings_dialog.view.width / 2,
            self._screen.get_height() / 2 - self._custom_settings_dialog.view.height / 2
        )
        self._scene_objects.append(self._custom_settings_dialog)
        
    def _open_about_dialog(self):
        self._about_dialog = AboutDialog(self._close_about_dialog)
        self._about_dialog.view.set_xy(
            self._screen.get_width() / 2 - self._about_dialog.view.width / 2,
            self._screen.get_height() / 2 - self._about_dialog.view.height / 2
        )
        self._scene_objects.append(self._about_dialog)  
        
    def _close_about_dialog(self):
        self._scene_objects.remove(self._about_dialog)
        self._about_dialog = None
        
    def _open_key_binding_dialog(self):
        self._key_binding_dialog = KeyBindingDialog(self._close_key_binding_dialog)
        self._key_binding_dialog.view.set_xy(
            self._screen.get_width() / 2 - self._key_binding_dialog.view.width / 2,
            self._screen.get_height() / 2 - self._key_binding_dialog.view.height / 2
        )
        self._scene_objects.append(self._key_binding_dialog)              
        
    def _close_custom_settings_dialog(self):
        self._scene_objects.remove(self._custom_settings_dialog)
        self._custom_settings_dialog = None
        
    def _close_key_binding_dialog(self):
        self._scene_objects.remove(self._key_binding_dialog)
        self._key_binding_dialog = None        
            
    def _start_game(self, config):
            if self._custom_settings_dialog is not None:
                self._custom_config = self._custom_settings_dialog.config
            self._scenes['game'].config = config
            self._scenes['game'].start()
            
    def _start_how_to_play(self):
        self._scenes['how_to_play'].start()
            
    def update(self, current_time, events):
        if self._about_dialog is not None:
            self._about_dialog.update(current_time, events)
        elif self._custom_settings_dialog is not None:
            self._custom_settings_dialog.update(current_time, events)
        elif self._key_binding_dialog is not None:
            self._key_binding_dialog.update(current_time, events)
        else:
            for game_object in self._scene_objects:
                game_object.update(current_time, events)
