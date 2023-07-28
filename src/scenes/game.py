from os import path
import pygame
from random import randint

from lib.scene import Scene
from difficulty_levels import default_difficulty
from lib.game_event import GameEvent
from lib.game_event_type import GameEventType
from game_objects.game_over_dialog import GameOverDialog
from game_objects.page_manager import PageManager
from game_objects.process_manager import ProcessManager
from game_objects.score_manager import ScoreManager
from game_objects.uptime_manager import UptimeManager

class Game(Scene):
    def __init__(self, screen, scenes, config=default_difficulty['config']):      
        self._config = config
               
        self._current_time = 0
        
        self._process_manager = None
        self._page_manager = None

        self._game_over = False
        self._game_over_time = None
        self._game_over_dialog = None

        super().__init__(screen, scenes)
   
    @property
    def config(self):
        return self._config
   
    @property
    def game_over(self):
        return self._game_over
    
    @game_over.setter
    def game_over(self, value):
        self._game_over = value
        
    @property
    def process_manager(self):
        return self._process_manager
    
    @property
    def page_manager(self):
        return self._page_manager

    def _setup(self):
        self._game_objects = []
        
        self._game_over = False
        self._game_over_time = None
        self._game_over_dialog = None
        
        self._process_manager = ProcessManager(self)
        self._game_objects.append(self._process_manager)
        
        self._page_manager = PageManager(self)
        self._game_objects.append(self._page_manager)
        
        self._score_manager = ScoreManager(self)
        self._game_objects.append(self._score_manager)
        
        self._uptime_manager = UptimeManager(self, pygame.time.get_ticks())
        self._game_objects.append(self._uptime_manager)
        
    def _return_to_main_menu(self):
        self.stop()
        self._scenes['main_menu'].start()

    def _update(self, current_time, events):                        
        display_game_over_dialog = self._game_over and self._game_over_time is not None and current_time - self._game_over_time > 1000

        if self._game_over:
            if self._game_over_time is None:
                self._game_over_time = current_time
            elif display_game_over_dialog:
                if self._game_over_dialog is None:
                    self._game_over_dialog = GameOverDialog(
                        self._uptime_manager.uptime_text, self._score_manager.score, self._setup, self._return_to_main_menu
                    )
                    self._game_over_dialog.view.set_xy(
                        (self._screen.get_width() - self._game_over_dialog.view.width) / 2, (self._screen.get_height() - self._game_over_dialog.view.height) / 2
                    )
                    self._game_objects.append(self._game_over_dialog)
                self._game_over_dialog.update(current_time, events)
        else:  
            for game_object in self._game_objects:
                game_object.update(current_time, events)
