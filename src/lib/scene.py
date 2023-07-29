import pygame
import sys

from abc import ABC, abstractmethod
from lib.game_event import GameEvent
from lib.game_event_type import GameEventType
from lib.ui.color import Color

class Scene(ABC):
    def __init__(self, screen, scenes, background_color=Color.BLACK):
        self._screen = screen
        self._scenes = scenes
        self._background_color = background_color
        self._is_started = False
        self._scene_objects = []
    
    @property
    def current_time(self):
        return pygame.time.get_ticks()
    
    def start(self):
        self._setup()
        self._is_started = True
        self._main_loop()
        
    def stop(self):
        self._is_started = False
    
    @abstractmethod
    def _setup(self):
        pass
    
    def _main_loop(self):
        while self._is_started:
            events = []
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    if (event.button == 1):
                        events.append(GameEvent(GameEventType.MOUSE_LEFT_CLICK, { 'position': event.pos }))
                        
            self._update(self.current_time, events)
            self._render()
    
    @abstractmethod
    def _update(self, current_time, events):
        pass
    
    def _render(self):      
        self._screen.fill(self._background_color)

        for game_object in self._scene_objects:
            game_object.render(self._screen)

        pygame.display.flip()
