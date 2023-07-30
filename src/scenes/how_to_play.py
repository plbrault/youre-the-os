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
        self._previous_button = None
        self._next_button = None
    
    def _setup(self):       
        self._scene_objects = []
        
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
            ),
            HowToPlayPart(
                [
                    'The same way, you can click on a running process to remove it from its CPU.',
                ],
                [
                    path.join('assets', 'how_to_play_4_0.png'),
                    path.join('assets', 'how_to_play_4_1.png')
                ]
            ),
            HowToPlayPart(
                [
                    'Over time, idle processes will go through 6 starvation levels.'
                ],
                [
                    path.join('assets', 'how_to_play_5_0.png'),
                    path.join('assets', 'how_to_play_5_1.png'),
                    path.join('assets', 'how_to_play_5_2.png'),
                    path.join('assets', 'how_to_play_5_3.png'),
                    path.join('assets', 'how_to_play_5_4.png'),
                    path.join('assets', 'how_to_play_5_5.png')
                ]
            ),
            HowToPlayPart(
                [
                    'Starvation levels help you know which processes have been idle the longest.',
                    'When a process stays idle for too long, the user becomes impatient and kills it.'
                ],
                [
                    path.join('assets', 'how_to_play_6_0.png'),
                    path.join('assets', 'how_to_play_6_1.png')
                ]
            ),
            HowToPlayPart(
                [
                    'Once the number of killed processes reaches 10, the user gets angry and reboots you.',
                    'The game is then over. Your goal is to survive as long as possible without getting rebooted!'
                ],
                [
                    path.join('assets', 'how_to_play_7_0.png')
                ]
            ),
            HowToPlayPart(
                [
                    'A process can also terminate gracefully. In that case, you can simply remove it by clicking on it.',
                    'Processes that terminate gracefully do not count towards your limit of 10 killed processes.'
                ],
                [
                    path.join('assets', 'how_to_play_8_0.png')
                ]
            ),
            HowToPlayPart(
                [
                    'Sometimes, a running process becomes blocked because it is waiting for an I/O event.',
                    'Blocked processes waste CPU time. It is a good idea to remove them from their CPU.',
                ],
                [
                    path.join('assets', 'how_to_play_9_0.png')
                ]
            ),
            HowToPlayPart(
                [
                    'When you have blocked processes, watch the I/O event bar.',
                    'Make sure to click on it when it has events, otherwise your processes will stay blocked and starve.'
                ],
                [
                    path.join('assets', 'how_to_play_10_0.png'),
                    path.join('assets', 'how_to_play_10_1.png')
                ]
            ),
            HowToPlayPart(
                [
                    'You also have to manage memory! Processes create memory pages when they run.',
                    'Pages that are currently in use appear in white. Currently unused pages appear in grey.'
                ],
                [
                    path.join('assets', 'how_to_play_11_0.png')
                ]
            ),
            HowToPlayPart(
                [
                    'Sometimes, you will run out of RAM and new pages will be written on disk.',
                    'You can swap pages between RAM and disk by clicking on them.'
                ],
                [
                    path.join('assets', 'how_to_play_12_0.png'),
                    path.join('assets', 'how_to_play_12_1.png')
                ]
            ),
            HowToPlayPart(
                [
                    'Processes can only use pages from RAM. A process will blink if trying to use pages that are on disk.',
                    'This is when you need to swap pages! The pages that the process is trying to access will also blink.'
                ],
                [
                    path.join('assets', 'how_to_play_13_0.png'),
                    path.join('assets', 'how_to_play_13_1.png')
                ],
                animation_interval=200
            )
        ]
        
        self._current_part_id = 0
        self._scene_objects.append(self._parts[self._current_part_id])
        
        self._previous_button = Button('<', self._go_to_previous_part)
        self._previous_button.view.set_xy(
            52,
            self._screen.get_height() - 62
        )
        self._scene_objects.append(self._previous_button)
        
        self._next_button = Button('>', self._go_to_next_part)
        self._next_button.view.set_xy(
            self._screen.get_width() - self._next_button.view.width - 52,
            self._screen.get_height() - 62
        )
        self._scene_objects.append(self._next_button)
    
    def _go_to_previous_part(self):
        if self._current_part_id == 0:
            self._return_to_main_menu()
        else:
            self._scene_objects.remove(self._previous_button)
            self._scene_objects.remove(self._next_button)
            self._scene_objects.remove(self._parts[self._current_part_id])
            
            self._current_part_id -= 1
            self._parts[self._current_part_id].initial_time = self.current_time
            
            self._scene_objects.append(self._parts[self._current_part_id])
            self._scene_objects.append(self._previous_button)
            self._scene_objects.append(self._next_button)
        
    def _go_to_next_part(self):
        if self._current_part_id == len(self._parts) - 1:
            self._return_to_main_menu()
        else:
            self._scene_objects.remove(self._previous_button)
            self._scene_objects.remove(self._next_button)
            self._scene_objects.remove(self._parts[self._current_part_id])
            
            self._current_part_id += 1
            self._parts[self._current_part_id].initial_time = self.current_time
            
            self._scene_objects.append(self._parts[self._current_part_id])
            self._scene_objects.append(self._previous_button)
            self._scene_objects.append(self._next_button)
    
    def _return_to_main_menu(self):
        self.stop()
        self._scenes['main_menu'].start()
    
    def _update(self, current_time, events):
        for game_object in self._scene_objects:
            game_object.update(current_time, events)
