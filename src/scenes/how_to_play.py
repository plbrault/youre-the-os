from os import path
import pygame
from random import randint

from lib.ui.color import Color
from game_objects.button import Button
from game_objects.how_to_play_part import HowToPlayPart
from lib.scene import Scene

class HowToPlay(Scene):
    def __init__(self, screen, scenes):
        super().__init__(screen, scenes, background_color=Color.LIGHT_GREY)
        
        self._parts = []
        self._current_part_id = 0
    
    def _setup(self):       
        self._game_objects = []
        
        self._parts = [
            HowToPlayPart(
                [
                    'In this game, you are the operating system of a computer.',
                    'You have to manage processes, memory, and input/output (I/O) events.'
                ], 
                [
                    path.join('assets', 'how_to_play_0_0.png')
                ]
            ),
            HowToPlayPart(
                [
                    'At the top of the screen, you can see your CPUs.'
                ],
                [
                    path.join('assets', 'how_to_play_1_0.png')
                ]
            ),
            HowToPlayPart(
                [
                    'Under your CPUs, you have the list of your idle processes.'
                ],
                [
                    path.join('assets', 'how_to_play_2_0.png')
                ]
            ),
            HowToPlayPart(
                [
                    'You can click on an idle process to assign it to an available CPU.',
                ],
                [
                    path.join('assets', 'how_to_play_3_0.png'),
                    path.join('assets', 'how_to_play_3_1.png')
                ]
            )
        ]
        
        self._current_part_id = 0
        self._game_objects.append(self._parts[self._current_part_id])
        
        previous_button = Button('<', self._go_to_previous_part)
        previous_button.view.set_xy(50, 10)
        self._game_objects.append(previous_button)
        
        next_button = Button('>', self._go_to_next_part)
        next_button.view.set_xy(self._screen.get_width() - next_button.view.width - 50, 10)
        self._game_objects.append(next_button)
    
    def _go_to_previous_part(self):
        if self._current_part_id == 0:
            self._return_to_main_menu()
        else:
            self._game_objects.remove(self._parts[self._current_part_id])
            self._current_part_id -= 1
            self._game_objects.append(self._parts[self._current_part_id])
        
    def _go_to_next_part(self):
        if self._current_part_id == len(self._parts) - 1:
            self._return_to_main_menu()
        else:
            self._game_objects.remove(self._parts[self._current_part_id])
            self._current_part_id += 1
            self._game_objects.append(self._parts[self._current_part_id])
    
    def _return_to_main_menu(self):
        self.stop()
        self._scenes['main_menu'].start()
    
    def _update(self, current_time, events):
        for game_object in self._game_objects:
            game_object.update(current_time, events)
