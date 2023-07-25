import os
import pygame
from random import randint
import sys

from lib.ui.color import Color
from lib.game_event import GameEvent
from lib.game_event_type import GameEventType
from game_objects.game_over_dialog import GameOverDialog
from game_objects.page_manager import PageManager
from game_objects.process_manager import ProcessManager
from game_objects.score_manager import ScoreManager
from game_objects.uptime_manager import UptimeManager

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        
        self._current_time = 0
        
        self._game_objects = []
        self._process_manager = None
        self._page_manager = None

        self._game_over = False
        self._game_over_time = None
        self._game_over_dialog = None

        self._window_width = 1024
        self._window_height = 768
        screen_size = self._window_width, self._window_height
        self._screen = pygame.display.set_mode(screen_size)

        icon = pygame.image.load(os.path.join('assets', 'icon.png'))
        pygame.display.set_caption("You're the OS!")
        pygame.display.set_icon(icon)

        self._setup()
        self._main_loop()

    @property
    def current_time(self):
        return self._current_time
    
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
        
        self._uptime_manager = UptimeManager(self)
        self._game_objects.append(self._uptime_manager)
        
        self._uptime_manager.reset()

    def _main_loop(self):
        while True:
            self._update(pygame.time.get_ticks())
            self._render()

    def _update(self, current_time):
        self._current_time = current_time
        
        events = []

        display_game_over_dialog = self._game_over and self._game_over_time is not None and current_time - self._game_over_time > 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if self._game_over and display_game_over_dialog:
                if event.type == pygame.KEYUP:
                    self._setup()
            elif not self._game_over:
                if event.type == pygame.MOUSEBUTTONUP:
                    if (event.button == 1):
                        events.append(GameEvent(GameEventType.MOUSE_LEFT_CLICK, { 'position': event.pos }))

        if self._game_over:
            if self._game_over_time is None:
                self._game_over_time = current_time
            elif display_game_over_dialog and self._game_over_dialog is None:
                self._game_over_dialog = GameOverDialog()
                self._game_over_dialog.view.set_xy(
                    (self._window_width - self._game_over_dialog.view.width) / 2, (self._window_height - self._game_over_dialog.view.height) / 2
                )
                self._game_objects.append(self._game_over_dialog)
        else:  
            for game_object in self._game_objects:
                game_object.update(current_time, events)

    def _render(self):
        self._screen.fill(Color.BLACK)

        for game_object in self._game_objects:
            game_object.render(self._screen)

        pygame.display.flip()
