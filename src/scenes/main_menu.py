from os import path
import pygame
from random import randint
import sys

from lib.scene import Scene
from lib.ui.color import Color
from game_objects.main_menu_title import MainMenuTitle

class MainMenu(Scene):
    def __init__(self, screen):
        super().__init__(screen)
        
    def _setup(self):
        self._game_objects = []
        
        title = MainMenuTitle()
        
        self._game_objects.append(title)
        
            
    def _update(self, current_time, events):
        pass
