from os import path
import pygame
from random import randint

from lib.ui.color import Color
from game_objects.how_to_play_part import HowToPlayPart
from lib.scene import Scene

class HowToPlay(Scene):
    def __init__(self, screen, scenes):
        super().__init__(screen, scenes, background_color=Color.LIGHT_GREY)
    
    def _setup(self):       
        part1 = HowToPlayPart(
            [
                'In this game, you are the operating system of a computer.',
                'You have to manage processes, memory, and input/output (I/O) events.'
            ], 
            [
                path.join('assets', 'how_to_play_0_0.png')
            ]
        )
        self._game_objects.append(part1)
            
    def _update(self, current_time, events):
        for game_object in self._game_objects:
            game_object.update(current_time, events)
