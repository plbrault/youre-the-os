from os import path
import pygame
from random import randint

from lib.ui.color import Color
from game_objects.how_to_play_part_1 import HowToPlayPart1
from lib.scene import Scene

class HowToPlay(Scene):
    def __init__(self, screen, scenes):
        super().__init__(screen, scenes, background_color=Color.LIGHT_GREY)
    
    def _setup(self):       
        part1 = HowToPlayPart1()
        self._game_objects.append(part1)
            
    def _update(self, current_time, events):
        for game_object in self._game_objects:
            game_object.update(current_time, events)
