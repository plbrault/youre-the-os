import pygame

from abc import ABC, abstractmethod
from lib.ui.color import Color

class Scene(ABC):
    def __init__(self, screen):
        self._screen = screen
        
        self._game_objects = []
        
        self._setup()
        self._main_loop()
    
    @abstractmethod
    def _setup(self):
        pass
    
    def _main_loop(self):
        while True:
            self._update(pygame.time.get_ticks())
            self._render()
    
    @abstractmethod
    def _update(self, current_time):
        pass
    
    def _render(self):      
        self._screen.fill(Color.BLACK)

        for game_object in self._game_objects:
            game_object.render(self._screen)

        pygame.display.flip()
