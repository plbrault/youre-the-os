from os import path
import pygame
from random import randint
import sys

from difficulty_levels import difficulty_levels
from lib.scene import Scene
from lib.ui.color import Color

class HowToPlay(Scene):
    def __init__(self, screen, scenes):
        super().__init__(screen, scenes)
    
    def _setup(self):
        pass
            
    def _update(self, current_time, events):
        for game_object in self._game_objects:
            game_object.update(current_time, events)
