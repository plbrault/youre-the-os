from os import path
import pygame
from random import randint
import sys

from lib.scene import Scene
from lib.ui.color import Color
from game_objects.button import Button
from game_objects.main_menu_title import MainMenuTitle

class MainMenu(Scene):
    def __init__(self, screen, scenes):
        super().__init__(screen, scenes)
    
    def _setup(self):
        self._game_objects = []
        
        title = MainMenuTitle()
        title.view.set_xy(0, 50)
        self._game_objects.append(title)
        
        play_button = Button('Play Game', self._start_game)
        play_button.view.set_xy((self._screen.get_width() - play_button.view.width) / 2, title.view.y + title.view.height + 200)
        self._game_objects.append(play_button)
        
    def _start_game(self):
        self.stop()
        self._scenes['game'].start()
            
    def _update(self, current_time, events):
        for game_object in self._game_objects:
            game_object.update(current_time, events)
