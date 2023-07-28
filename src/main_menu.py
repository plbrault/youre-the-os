from os import path
import pygame
from random import randint
import sys

from lib.ui.color import Color

class MainMenu:
    def __init__(self, screen):
        self._screen = screen
        
        self._game_objects = []
        
        self._setup()
        self._main_loop()
        
    def _setup(self):
        pass
    
    def _main_loop(self):
        while True:
            self._update(pygame.time.get_ticks())
            self._render()
            
    def _update(self, current_time):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                if (event.button == 1):
                    events.append(GameEvent(GameEventType.MOUSE_LEFT_CLICK, { 'position': event.pos }))
    
    def _render(self):
        self._screen.fill(Color.BLACK)

        for game_object in self._game_objects:
            game_object.render(self._screen)

        pygame.display.flip()
