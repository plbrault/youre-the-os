import pygame
import sys

from abc import ABC, abstractmethod
from lib.game_event import GameEvent
from lib.game_event_type import GameEventType
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
            events = []
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    if (event.button == 1):
                        events.append(GameEvent(GameEventType.MOUSE_LEFT_CLICK, { 'position': event.pos }))
                        
            self._update(pygame.time.get_ticks(), events)
            self._render()
    
    @abstractmethod
    def _update(self, current_time, events):
        pass
    
    def _render(self):      
        self._screen.fill(Color.BLACK)

        for game_object in self._game_objects:
            game_object.render(self._screen)

        pygame.display.flip()
