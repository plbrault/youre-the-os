from os import path
import pygame
from random import randint

from lib.scene import Scene
from difficulty_levels import default_difficulty
from lib.game_event import GameEvent
from lib.game_event_type import GameEventType
from game_objects.button import Button
from game_objects.game_over_dialog import GameOverDialog
from game_objects.in_game_menu_dialog import InGameMenuDialog
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

        self._in_game_menu_is_open = False
        self._in_game_menu_dialog = None

        self._game_over = False
        self._game_over_time = None
        self._game_over_dialog = None

        super().__init__(screen, scenes)

    def setup(self):
        self._scene_objects = []
        
        self._in_game_menu_is_open = False
        self._in_game_menu_dialog = None
        
        self._game_over = False
        self._game_over_time = None
        self._game_over_dialog = None
        
        self._process_manager = ProcessManager(self)
        self._page_manager = PageManager(self)
        
        self._process_manager.setup()
        self._scene_objects.append(self._process_manager)
        
        self._page_manager.setup()
        self._scene_objects.append(self._page_manager)
        
        self._score_manager = ScoreManager(self)
        self._scene_objects.append(self._score_manager)
        
        self._uptime_manager = UptimeManager(self, pygame.time.get_ticks())
        self._scene_objects.append(self._uptime_manager)
        
        open_in_game_menu_button = Button('Menu', self._open_in_game_menu)
        open_in_game_menu_button.view.set_xy(
            self._screen.get_width() - open_in_game_menu_button.view.width - 10,
            10
        )
        self._scene_objects.append(open_in_game_menu_button)
   
    @property
    def config(self):
        return self._config
    
    @config.setter
    def config(self, value):
        self._config = value
   
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
   
    def _open_in_game_menu(self):
        self._in_game_menu_is_open = True
        if self._in_game_menu_dialog is None:
            self._in_game_menu_dialog = InGameMenuDialog(self.setup, self._return_to_main_menu, self._close_in_game_menu)
            self._in_game_menu_dialog.view.set_xy(
                (self._screen.get_width() - self._in_game_menu_dialog.view.width) / 2,
                (self._screen.get_height() - self._in_game_menu_dialog.view.height) / 2
            )
            self._scene_objects.append(self._in_game_menu_dialog)
        self._uptime_manager.pause()
        
    def _close_in_game_menu(self):
        self._in_game_menu_is_open = False
        self._scene_objects.remove(self._in_game_menu_dialog)
        self._in_game_menu_dialog = None
        self._uptime_manager.resume()
        
    def _return_to_main_menu(self):
        self._scenes['main_menu'].start()

    def update(self, current_time, events):
        dialog = None
            
        if self._in_game_menu_is_open:
            dialog = self._in_game_menu_dialog
        elif self._game_over:
            display_game_over_dialog = self._game_over_time is not None and current_time - self._game_over_time > 1000
            if self._game_over_time is None:
                self._game_over_time = current_time
            elif display_game_over_dialog:
                if self._game_over_dialog is None:
                    self._game_over_dialog = GameOverDialog(
                        self._uptime_manager.uptime_text, self._score_manager.score, self.setup, self._return_to_main_menu
                    )
                    self._game_over_dialog.view.set_xy(
                        (self._screen.get_width() - self._game_over_dialog.view.width) / 2,
                        (self._screen.get_height() - self._game_over_dialog.view.height) / 2
                    )
                    self._scene_objects.append(self._game_over_dialog)
                dialog = self._game_over_dialog
        
        if dialog is not None:
            dialog.update(current_time, events)
        else:
            for game_object in self._scene_objects:
                game_object.update(current_time, events)
