from os import path
import pygame
from random import randint
import sys

from difficulty_levels import difficulty_levels
from lib.scene import Scene
from lib.ui.color import Color
from game_objects.button import Button
from game_objects.main_menu_title import MainMenuTitle
from game_objects.difficulty_selection_label import DifficultySelectionLabel
from game_objects.option_selector import OptionSelector

class MainMenu(Scene):
    def __init__(self, screen, scenes):
        super().__init__(screen, scenes)
    
    def _setup(self):
        self._game_objects = []
        
        title = MainMenuTitle()
        title.view.set_xy(0, 50)
        self._game_objects.append(title)
        
        difficulty_selection_label = DifficultySelectionLabel()
        difficulty_selection_label.view.set_xy(
            (self._screen.get_width() - difficulty_selection_label.view.width) / 2,
            title.view.y + title.view.height + 50
        )
        self._game_objects.append(difficulty_selection_label)
        
        self._difficulty_selector = OptionSelector(
            list(map(lambda difficulty_level: difficulty_level['name'], difficulty_levels)),
            1
        )
        self._difficulty_selector.view.set_xy(
            (self._screen.get_width() - self._difficulty_selector.view.width) / 2,
            difficulty_selection_label.view.y + difficulty_selection_label.view.height + 20
        )
        self._game_objects.append(self._difficulty_selector)
        
        play_button = Button('Play', self._start_game)
        play_button.view.set_xy(
            (self._screen.get_width() - play_button.view.width) / 2,
            self._difficulty_selector.view.y + self._difficulty_selector.view.height + 20
        )
        self._game_objects.append(play_button)
        
    def _start_game(self):
        self.stop()
        self._scenes['game'].config = difficulty_levels[self._difficulty_selector.selected_option_id]['config']
        self._scenes['game'].start()
            
    def _update(self, current_time, events):
        for game_object in self._game_objects:
            game_object.update(current_time, events)
